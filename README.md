# Tronds Radar

Overvåker norske nyheter langs kysten (Oslofjorden til Vardø) daglig og
løfter fram saker som kan bety oppdrag for Tronds Marine Service: havari og
berging, ny kai/bru/kabel-infrastruktur, oppdrettsanlegg som bygges om, og
industri/decommissioning med tungløft over sjø.

## Hvordan det virker

1. `radar/sources.py` - liste over kilder: direkte RSS (iLaks, TU.no, NRK
   distriktssendinger, Havarikommisjonen) + Google News RSS som fallback
   (brede søk på nøkkelord, samt `site:`-søk for bransjemedier/myndigheter
   uten egen fungerende RSS-feed).
2. `radar/normalize.py` + `radar/keywords.py` - matcher hver artikkeltittel
   (+ evt. sammendrag) mot nøkkelord i fire kategorier. Håndterer at
   vestlandsaviser skriver nynorsk mens søkeordene er bokmål (f.eks.
   "grunnstøyting"/"grunnstøting", "leggjast"/"legges").
3. `radar/fetch.py` - henter og parser feedene.
4. `radar/dedupe.py` - filtrerer bort artikler eldre enn 48 timer og saker
   som allerede er vist før (historikk i `data/history.json`, committes av
   workflowen).
5. `radar/render.py` - skriver `docs/index.html`, en enkel side gruppert
   per kategori med overskrift + lenke + kilde, som viser siste 7 dager.
6. `radar/email_digest.py` - sender en e-post-digest hvis SMTP er
   konfigurert via miljøvariabler/secrets (se under). Hopper stille over
   hvis ikke.
7. `.github/workflows/daily.yml` - kjører alt dette automatisk hver dag.

## Oppsett (én gang)

1. Push dette repoet til GitHub (privat eller offentlig, etter behov).
2. Under **Settings > Pages**: velg "Deploy from a branch", branch
   `main`, mappe `/docs`. Etter neste kjøring er siden tilgjengelig på
   `https://<bruker>.github.io/<repo>/`.
3. (Valgfritt) For e-post-digest, legg til disse secrets under
   **Settings > Secrets and variables > Actions**:
   `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`,
   `EMAIL_TO` (kommaseparert liste). Uten disse kjører alt som normalt,
   bare uten e-postutsendelse.
4. Workflowen kjører automatisk hver dag (05:30 UTC) og kan også startes
   manuelt fra "Actions"-fanen ("Run workflow").

## Kjøre lokalt

```
pip install -r requirements.txt
python -m radar.main
```

Skriver/oppdaterer `data/history.json` og `docs/index.html`.

## Justere treffsikkerhet

- Legg til/fjern kilder i `radar/sources.py`.
- Legg til/fjern nøkkelord i `radar/keywords.py`. Enkeltord som er
  tvetydige alene (f.eks. "løftes", "heves", "vrak") ligger i `VERB_STEMS`
  og krever et fartøys-/anleggsord i samme tekst (`_EXTRA_ANCHOR_NOUNS`)
  for å telle som treff - se kommentarene i filen for eksempler på hvorfor.
