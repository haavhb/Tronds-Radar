"""Henter og parser RSS/Atom-feeds, og matcher innhold mot nøkkelord."""

import calendar
import logging
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import feedparser
import requests

from radar.keywords import match_categories

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (compatible; TrondsRadar/1.0; "
    "+https://github.com/) TrondsRadar-nyhetsovervaking"
)
_TIMEOUT_SECONDS = 15
_MAX_RETRIES = 2
_ALLOWED_LINK_SCHEMES = {"http", "https"}


def _is_safe_link(link: str) -> bool:
    """Avviser lenker med andre skjema enn http(s), f.eks. javascript:-URIer
    som en kompromittert eller ondsinnet feed kunne forsøkt å smugle inn."""
    try:
        return urlparse(link).scheme in _ALLOWED_LINK_SCHEMES
    except ValueError:
        return False


@dataclass
class Hit:
    title: str
    link: str
    source_name: str
    published: str  # RFC/ISO-streng slik feeden oppga den, kan være tom
    published_ts: float | None = None  # epoch-sekunder, for ferskhetsfilter
    categories: list[str] = field(default_factory=list)


def _fetch_bytes(url: str) -> bytes | None:
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url, headers={"User-Agent": _USER_AGENT}, timeout=_TIMEOUT_SECONDS
            )
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as exc:
            logger.warning("Feil ved henting av %s (forsøk %d): %s", url, attempt, exc)
            if attempt < _MAX_RETRIES:
                time.sleep(1.5)
    return None


def fetch_source(source: dict[str, str]) -> list[Hit]:
    """Henter én kilde og returnerer treffene som matcher minst én kategori."""
    raw = _fetch_bytes(source["url"])
    if raw is None:
        logger.error("Ga opp å hente %s (%s)", source["name"], source["url"])
        return []

    parsed = feedparser.parse(raw)
    if parsed.bozo and not parsed.entries:
        logger.warning("Kunne ikke tolke feed %s (%s): %s", source["name"], source["url"], parsed.bozo_exception)
        return []

    hits = []
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link or not _is_safe_link(link):
            continue
        summary = entry.get("summary", "") or ""
        text = f"{title} {summary}"
        categories = match_categories(text)
        if not categories:
            continue
        published = entry.get("published", "") or entry.get("updated", "")
        struct = entry.get("published_parsed") or entry.get("updated_parsed")
        published_ts = calendar.timegm(struct) if struct else None
        hits.append(
            Hit(
                title=title,
                link=link,
                source_name=source["name"],
                published=published,
                published_ts=published_ts,
                categories=categories,
            )
        )
    return hits


def fetch_all(sources: list[dict[str, str]]) -> list[Hit]:
    """Henter alle kilder sekvensielt og samler treffene. Feil i én kilde
    stopper ikke resten."""
    all_hits: list[Hit] = []
    for source in sources:
        try:
            all_hits.extend(fetch_source(source))
        except Exception:
            logger.exception("Uventet feil ved henting av %s", source["name"])
    return all_hits
