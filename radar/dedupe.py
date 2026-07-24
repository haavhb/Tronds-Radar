"""Historikk og dedup for Tronds Radar.

Historikken lagres som JSON: {dedupe_key: {first_seen, title, link,
source_name, categories, published}}. Filen committes til repoet av GitHub
Actions-workflowen slik at dedup fungerer på tvers av kjøringer uten en egen
database, og slik at render.py kan vise en rullerende periode (ikke bare
dagens funn) uten å kjøre alle kildene på nytt.

To uavhengige filtre på hvert nytt fetch-resultat:
- Ferskhet: artikler eldre enn MAX_AGE_HOURS (basert på feedens pubDato)
  ekskluderes helt før de når historikken. Artikler uten parsbar dato
  slipper gjennom, siden vi ikke kan bevise at de er gamle.
- Dedup: en sak vi allerede har sett (samme normaliserte tittel) legges ikke
  inn på nytt. Historikken pruned etter HISTORY_RETENTION_DAYS for å holde
  filen liten - dette er et vedlikeholdshensyn, ikke en bevisst
  gjenåpning for gamle saker.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from radar.fetch import Hit

MAX_AGE_HOURS = 48
HISTORY_RETENTION_DAYS = 30

_WS_RE = re.compile(r"\s+")

HistoryRecord = dict


def _dedupe_key(hit: Hit) -> str:
    normalized_title = _WS_RE.sub(" ", hit.title.strip().lower())
    return normalized_title


def load_history(path: Path) -> dict[str, HistoryRecord]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_history(path: Path, history: dict[str, HistoryRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )


def _prune(history: dict[str, HistoryRecord], now: datetime) -> dict[str, HistoryRecord]:
    cutoff = now.timestamp() - HISTORY_RETENTION_DAYS * 86400
    pruned = {}
    for key, record in history.items():
        try:
            seen_ts = datetime.fromisoformat(record["first_seen"]).timestamp()
        except (KeyError, ValueError, TypeError):
            continue
        if seen_ts >= cutoff:
            pruned[key] = record
    return pruned


def filter_new(
    hits: list[Hit], history: dict[str, HistoryRecord], now: datetime | None = None
) -> tuple[list[Hit], dict[str, HistoryRecord]]:
    """Filtrerer bort for gamle og allerede sette treff, og oppdaterer historikken.

    Returnerer (nye_treff, oppdatert_historikk). Historikken må lagres av
    kalleren (save_history) for at dedup og siden skal fungere neste kjøring.
    """
    now = now or datetime.now(timezone.utc)
    cutoff_ts = now.timestamp() - MAX_AGE_HOURS * 3600

    updated_history = _prune(dict(history), now)
    new_hits = []
    for hit in hits:
        if hit.published_ts is not None and hit.published_ts < cutoff_ts:
            continue
        key = _dedupe_key(hit)
        if key in updated_history:
            continue
        new_hits.append(hit)
        updated_history[key] = {
            "first_seen": now.isoformat(),
            "title": hit.title,
            "link": hit.link,
            "source_name": hit.source_name,
            "categories": hit.categories,
            "published": hit.published,
        }
    return new_hits, updated_history
