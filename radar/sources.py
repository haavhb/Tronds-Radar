"""Kildeliste for Tronds Radar.

To slags kilder:

1. DIRECT_FEEDS: RSS-feeds vi har verifisert fungerer direkte (returnerer
   200 og gyldig RSS/Atom). Disse er generelle nyhetsfeeds (ikke forhånds-
   filtrert), så alt herfra går gjennom radar.keywords.match_categories.

2. Google News RSS som fallback/utvidelse, i to varianter:
   - GOOGLE_NEWS_KEYWORD_QUERIES: brede, landsdekkende søk på sentrale
     begreper (bokmål + nynorsk-former der de skiller seg fra hverandre).
     Google Nyheter indekserer de aller fleste norske lokalaviser, så dette
     er hovedkilden til bred kystdekning uten å måtte liste opp hver
     lokalavis manuelt.
   - GOOGLE_NEWS_SITE_QUERIES: site:-avgrensede søk for bransjemedier og
     myndigheter som ikke har en fungerende offentlig RSS-feed (verifisert
     ved manuell sjekk av /feed, /rss og vanlige varianter).

Alle Google News-URLer bygges med hl=no&gl=NO&ceid=NO:no for norske
resultater. Artikkellenkene som kommer tilbake er Googles egne
redirect-lenker (news.google.com/rss/articles/...), som fungerer fint for
"overskrift + lenke"-bruk.
"""

import urllib.parse

DIRECT_FEEDS: list[dict[str, str]] = [
    {"name": "iLaks", "url": "https://ilaks.no/feed/"},
    {"name": "Teknisk Ukeblad (TU.no)", "url": "https://www.tu.no/rss"},
    {"name": "Statens havarikommisjon (NSIA)", "url": "https://www.nsia.no/rss?type=0"},
    # NRK distriktssendinger, Oslofjorden rundt kysten til Vardø.
    {"name": "NRK Østlandssendingen", "url": "https://www.nrk.no/ostlandssendingen/toppsaker.rss"},
    {"name": "NRK Vestfold og Telemark", "url": "https://www.nrk.no/vestfoldogtelemark/toppsaker.rss"},
    {"name": "NRK Sørlandet", "url": "https://www.nrk.no/sorlandet/toppsaker.rss"},
    {"name": "NRK Rogaland", "url": "https://www.nrk.no/rogaland/toppsaker.rss"},
    {"name": "NRK Vestland", "url": "https://www.nrk.no/vestland/toppsaker.rss"},
    {"name": "NRK Møre og Romsdal", "url": "https://www.nrk.no/mr/toppsaker.rss"},
    {"name": "NRK Trøndelag", "url": "https://www.nrk.no/trondelag/toppsaker.rss"},
    {"name": "NRK Nordland", "url": "https://www.nrk.no/nordland/toppsaker.rss"},
    {"name": "NRK Troms og Finnmark", "url": "https://www.nrk.no/tromsogfinnmark/toppsaker.rss"},
]

_GOOGLE_NEWS_BASE = "https://news.google.com/rss/search"


def _google_news_url(query: str) -> str:
    params = {"q": query, "hl": "no", "gl": "NO", "ceid": "NO:no"}
    return f"{_GOOGLE_NEWS_BASE}?{urllib.parse.urlencode(params)}"


# Brede søk, gruppert per kategori (kategorien brukes kun til visning/logging
# - reell kategorisering skjer uansett via match_categories på treffet).
GOOGLE_NEWS_KEYWORD_QUERIES: list[dict[str, str]] = [
    {
        "name": "GNews: grunnstøting/forlis",
        "category_hint": "havari_berging",
        "query": '"grunnstøting" OR "grunnstøyting" OR "grunnstøtt" OR "grunnstøytt" OR "forlis"',
    },
    {
        "name": "GNews: kantring/vrak/berging",
        "category_hint": "havari_berging",
        "query": '"kantret" OR "kantring" OR "vraket" OR "berging av fartøy" OR "heve vraket"',
    },
    {
        "name": "GNews: slep/nødhavn",
        "category_hint": "havari_berging",
        "query": '"slepebåt" OR "nødhavn" OR "drivende fartøy" OR "brann om bord"',
    },
    {
        "name": "GNews: ny kai/molo/bru",
        "category_hint": "infrastruktur",
        "query": '"ny ferjekai" OR "ny kai" OR "ny molo" OR "brufundament"',
    },
    {
        "name": "GNews: sjøkabel/sjøledning",
        "category_hint": "infrastruktur",
        "query": '"sjøkabel" OR "sjøledning" OR "undersjøisk kabel" OR "kabellegging"',
    },
    {
        "name": "GNews: ny lokalitet/konsesjon oppdrett",
        "category_hint": "oppdrett",
        "query": '"ny lokalitet" oppdrett OR "oppdrettskonsesjon" OR "fôrflåte"',
    },
    {
        "name": "GNews: merder/fortøyning skiftes",
        "category_hint": "oppdrett",
        "query": '"merdene skal skiftes" OR "merdane skal skiftast" OR "fortøyningsanlegg"',
    },
    {
        "name": "GNews: decommissioning/tungløft",
        "category_hint": "industri",
        "query": '"decommissioning" Norge OR "modultransport" OR "tungløft"',
    },
    {
        "name": "GNews: riving/plattform fjernes",
        "category_hint": "industri",
        "query": '"fabrikk skal rives" OR "rive fabrikken" OR "plattform skal fjernes"',
    },
]

# site:-avgrensede søk som erstatning for feeds som ikke har fungerende RSS.
_SITE_QUERY_DOMAINS: list[tuple[str, str]] = [
    ("Kyst.no", "kyst.no"),
    ("Fiskeribladet", "fiskeribladet.no"),
    ("Bygg.no", "bygg.no"),
    ("Skipsrevyen", "skipsrevyen.no"),
    ("Sysla", "sysla.no"),
    ("Kystverket", "kystverket.no"),
    ("Sjøfartsdirektoratet", "sdir.no"),
    ("IntraFish", "intrafish.no"),
]

GOOGLE_NEWS_SITE_QUERIES: list[dict[str, str]] = [
    {
        "name": f"GNews site: {name}",
        "category_hint": None,
        "query": f"site:{domain}",
    }
    for name, domain in _SITE_QUERY_DOMAINS
]


def all_sources() -> list[dict[str, str]]:
    """Returnerer alle kilder som en flat liste med name/url/kind."""
    sources = []
    for feed in DIRECT_FEEDS:
        sources.append({"name": feed["name"], "url": feed["url"], "kind": "direct"})
    for gq in GOOGLE_NEWS_KEYWORD_QUERIES:
        sources.append(
            {"name": gq["name"], "url": _google_news_url(gq["query"]), "kind": "google_news"}
        )
    for gq in GOOGLE_NEWS_SITE_QUERIES:
        sources.append(
            {"name": gq["name"], "url": _google_news_url(gq["query"]), "kind": "google_news"}
        )
    return sources
