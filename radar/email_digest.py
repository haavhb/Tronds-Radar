"""E-post-digest for Tronds Radar - av og på via miljøvariabler.

E-postoppsett (avsender/mottakere/SMTP) var ikke avklart da resten av
verktøyet ble bygget, så sending er utsatt og konfigurerbar:

Sett følgende miljøvariabler (f.eks. som GitHub Actions secrets) for å slå
på utsendelse. Mangler noen av dem, hopper vi stille over sending - siden
(GitHub Pages) er alltid hovedkanalen uansett.

  SMTP_HOST       - f.eks. smtp.gmail.com
  SMTP_PORT       - f.eks. 587
  SMTP_USER       - brukernavn for autentisering
  SMTP_PASSWORD   - passord/app-passord
  EMAIL_FROM      - avsenderadresse
  EMAIL_TO        - mottakere, kommaseparert

Sending er "best effort": feiler den, logges det, men resten av kjøringen
(historikk + nettside) er allerede fullført og påvirkes ikke.
"""

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from radar.fetch import Hit
from radar.keywords import CATEGORIES

logger = logging.getLogger(__name__)

_REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
]


def _is_configured() -> bool:
    return all(os.environ.get(var) for var in _REQUIRED_ENV_VARS)


def _build_body(hits: list[Hit]) -> str:
    lines = ["Nye treff fra Tronds Radar:", ""]
    for cat_key, cat_title in CATEGORIES.items():
        cat_hits = [h for h in hits if cat_key in h.categories]
        if not cat_hits:
            continue
        lines.append(f"== {cat_title} ==")
        for h in cat_hits:
            lines.append(f"- {h.title}")
            lines.append(f"  {h.link} ({h.source_name})")
        lines.append("")
    return "\n".join(lines)


def maybe_send_digest(new_hits: list[Hit], now: datetime | None = None) -> None:
    if not new_hits:
        logger.info("Ingen nye treff - hopper over e-post.")
        return
    if not _is_configured():
        logger.info("E-post ikke konfigurert (mangler miljøvariabler) - hopper over sending.")
        return

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    sender = os.environ["EMAIL_FROM"]
    recipients = [addr.strip() for addr in os.environ["EMAIL_TO"].split(",") if addr.strip()]

    msg = EmailMessage()
    msg["Subject"] = f"Tronds Radar - {len(new_hits)} nye treff"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(_build_body(new_hits))

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        logger.info("Sendte e-post-digest til %s", ", ".join(recipients))
    except Exception:
        logger.exception("Klarte ikke å sende e-post-digest")
