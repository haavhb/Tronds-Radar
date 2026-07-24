"""Genererer docs/index.html - den statiske siden salgsavdelingen sjekker.

Siden viser en rullerende periode (DISPLAY_DAYS) hentet fra hele
historikk-filen, ikke bare dagens kjøring, slik at siden har innhold å vise
selv rett etter en stille dag.
"""

import html
from datetime import datetime, timezone
from pathlib import Path

from radar.dedupe import HistoryRecord
from radar.keywords import CATEGORIES

DISPLAY_DAYS = 7

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tronds Radar</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
         max-width: 780px; margin: 0 auto; padding: 24px 16px 64px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 0; }}
  .subtitle {{ color: #666; font-size: 0.9rem; margin-top: 4px; }}
  .category {{ margin-top: 32px; }}
  .category h2 {{ font-size: 1.15rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 6px; }}
  .count {{ color: #888; font-weight: normal; font-size: 0.9rem; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{ padding: 12px 0; border-bottom: 1px solid #e0e0e0; }}
  li a {{ color: #0b4f8a; text-decoration: none; font-weight: 600; }}
  li a:hover {{ text-decoration: underline; }}
  .meta {{ color: #888; font-size: 0.82rem; margin-top: 2px; }}
  .empty {{ color: #888; font-style: italic; }}
  footer {{ margin-top: 48px; color: #999; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>Tronds Radar</h1>
<p class="subtitle">Nyheter som kan bety oppdrag for Tronds Marine Service.
Viser treff fra siste {display_days} dager. Generert {generated}.</p>
{sections}
<footer>Overskrift og lenke er nok til å vurdere om saken er relevant &mdash; gå videre selv for detaljer.</footer>
</body>
</html>
"""

_SECTION_TEMPLATE = """<div class="category">
  <h2>{title} <span class="count">({count})</span></h2>
  {body}
</div>
"""


def _format_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return ""
    return dt.strftime("%d.%m.%Y %H:%M")


def render_page(history: dict[str, HistoryRecord], now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    cutoff_ts = now.timestamp() - DISPLAY_DAYS * 86400

    records = [r for r in history.values() if _record_ts(r) >= cutoff_ts]
    records.sort(key=_record_ts, reverse=True)

    sections = []
    for cat_key, cat_title in CATEGORIES.items():
        cat_records = [r for r in records if cat_key in r.get("categories", [])]
        if cat_records:
            items = "\n".join(
                f'  <li><a href="{html.escape(r["link"])}" rel="noopener" target="_blank">'
                f'{html.escape(r["title"])}</a>'
                f'<div class="meta">{html.escape(r["source_name"])} &middot; '
                f'{_format_date(r["first_seen"])}</div></li>'
                for r in cat_records
            )
            body = f"<ul>\n{items}\n</ul>"
        else:
            body = '<p class="empty">Ingen treff siste periode.</p>'
        sections.append(
            _SECTION_TEMPLATE.format(title=html.escape(cat_title), count=len(cat_records), body=body)
        )

    return _PAGE_TEMPLATE.format(
        display_days=DISPLAY_DAYS,
        generated=now.strftime("%d.%m.%Y %H:%M UTC"),
        sections="\n".join(sections),
    )


def _record_ts(record: HistoryRecord) -> float:
    try:
        return datetime.fromisoformat(record["first_seen"]).timestamp()
    except (KeyError, ValueError, TypeError):
        return 0.0


def write_page(history: dict[str, HistoryRecord], output_path: Path, now: datetime | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_page(history, now=now), encoding="utf-8")
