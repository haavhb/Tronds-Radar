"""Orkestrerer en full kjøring av Tronds Radar.

1. Hent alle kilder (radar.sources)
2. Match mot nøkkelord (skjer allerede inni radar.fetch)
3. Filtrer bort for gamle/allerede sette treff (radar.dedupe)
4. Oppdater historikken og skriv den statiske siden (radar.render)
5. Bygg e-post-digest hvis SMTP er konfigurert (radar.email_digest)
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from radar.dedupe import filter_new, load_history, save_history
from radar.email_digest import maybe_send_digest
from radar.fetch import fetch_all
from radar.render import write_page
from radar.sources import all_sources

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_PATH = REPO_ROOT / "data" / "history.json"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "index.html"


def run() -> int:
    now = datetime.now(timezone.utc)
    sources = all_sources()
    logger.info("Henter %d kilder...", len(sources))
    hits = fetch_all(sources)
    logger.info("Fikk %d råtreff (matchet minst én kategori) før dedup/ferskhet.", len(hits))

    history = load_history(HISTORY_PATH)
    new_hits, updated_history = filter_new(hits, history, now=now)
    logger.info("%d nye treff etter dedup/ferskhetsfilter.", len(new_hits))

    save_history(HISTORY_PATH, updated_history)
    write_page(updated_history, DOCS_INDEX_PATH, now=now)
    logger.info("Skrev %s", DOCS_INDEX_PATH)

    maybe_send_digest(new_hits, now=now)
    return 0


if __name__ == "__main__":
    sys.exit(run())
