"""Nøkkelord-kategorier for Tronds Radar.

Enkeltord-stammer brukes for begreper som er spesifikke nok til sjelden å gi
falske treff (f.eks. "grunnstøt", "merd", "fôrflåte"). Vanlige/tvetydige ord
("heve", "senke", "kollisjon", "lokalitet", "konsesjon", "modul" osv.) er
bare med som flerords-uttrykk, forankret til en maritim/marin kontekst, for
å unngå at f.eks. "heve renten" eller "ny lokalitet for barnehage" gir treff.

Stammer normaliseres via radar.normalize slik at bokmål- og nynorskformer
(løftes/løftast, skiftes/skiftast, leggjast/legges, grunnstøting/
grunnstøyting) fanges av samme oppslag.
"""

from radar.normalize import normalize_text, normalize_word

CATEGORIES = {
    "havari_berging": "Havari, grunnstøting og berging",
    "infrastruktur": "Kai, bru, kabel og sjøledning",
    "oppdrett": "Oppdrett: lokaliteter, merder og fortøyning",
    "industri": "Industri: riving, decommissioning og tungløft",
}

# Enkeltord-stammer (lav tvetydighet).
STEM_KEYWORDS: dict[str, list[str]] = {
    "havari_berging": [
        # NB: "vrak" er bevisst utelatt som frittstående stamme - det er
        # tvetydig med verbet "å vrake" (forkaste, som i "velge og vrake",
        # "vraket forslaget"). Fanges i stedet opp via VERB_STEMS lenger
        # ned, som krever et fartøysord i samme tekst.
        "grunnstøt", "grunnstøyt", "forlis", "forlist", "kantr",
        "slepebåt", "nødhavn", "synkeferdig", "havarikommisjon",
    ],
    "infrastruktur": [
        "kai", "molo", "ferjekai", "fergekai", "brufundament",
        "sjøledning", "sjøkabel", "sjøkabling", "kabellegging",
        "rørledning",
    ],
    "oppdrett": [
        # NB: "oppdrett" er bevisst utelatt som frittstående stamme - det er
        # for generelt (matcher praktisk talt alt fra bransjepressen, inkl.
        # ren finansnyheter), og fanges likevel opp via mer spesifikke
        # substantiv og fraser under.
        "merd", "fôrflåte", "forflåte", "fortøy", "akvakultur",
        "slaktemerd", "notpose",
    ],
    "industri": [
        "riving", "rivast", "rives", "revet",
        "decommission", "nedstenging", "modultransport",
        "tungløft", "tungloft", "smelteverk", "prosessanlegg",
    ],
}

# Flerords-uttrykk (matches som substring i rå, lowercased tekst). Brukes
# for ord som er for generelle til å stå alene.
PHRASE_KEYWORDS: dict[str, list[str]] = {
    "havari_berging": [
        "heve vraket", "heve fartøyet", "heve skipet", "heve båten",
        "berge fartøyet", "berging av fartøy", "berging til sjøs",
        "bergingsaksjon", "sunket fartøy", "sank utenfor", "senket fartøy",
        "gikk ned utenfor", "kollisjon til sjøs", "kollisjon mellom fartøy",
        "kollisjon med skip", "brann om bord", "lekkasje om bord",
        "drivende fartøy", "drivende båt", "assistanse til nødstedt",
    ],
    "infrastruktur": [
        "ny kai", "ny molo", "kai skal bygges", "molo skal bygges",
        "undersjøisk kabel", "sjøkabel skal legges", "ferjekai skal",
        "kaianlegg", "ferjesamband", "bru over fjorden", "brufundament",
    ],
    "oppdrett": [
        "ny lokalitet", "lokalitet for oppdrett", "utvidelse av lokalitet",
        "oppdrettskonsesjon", "konsesjon for oppdrett", "fôrflåte skal",
        "merder skal", "flytte anlegget", "skifte merder",
    ],
    "industri": [
        "modul skal fraktes", "modul skal løftes", "plattform skal fjernes",
        "fabrikk skal rives", "rive fabrikken", "tungt utstyr skal fraktes",
        "sjøtransport av modul",
    ],
}

# Uregelmessige nynorskformer som normaliseringsreglene ikke fanger
# automatisk (listes opp som ekstra stammer per kategori).
_EXTRA_NYNORSK_STEMS = {
    "oppdrett": ["flytj"],  # flytjast (nynorsk) vs flyttes (bokmål)
}
for _cat, _extra in _EXTRA_NYNORSK_STEMS.items():
    STEM_KEYWORDS[_cat].extend(_extra)

# Verb som er for generiske til å telle alene ("løftes", "legges", "skiftes"
# er vanlige ord i alle slags sammenhenger), men som er sterke signaler når de
# opptrer sammen med et forankrende substantiv fra samme kategori i samme
# tekst. Dekker eksplisitt løftast/leggjast/skiftast fra oppdraget.
VERB_STEMS: dict[str, list[str]] = {
    "havari_berging": ["vrak"],  # vraket (skipsvrak) vs. vraket (forkastet) - krever fartøysord
    "infrastruktur": ["legg"],  # sjøkabelen skal leggjast/legges
    "oppdrett": ["skift"],  # merdene skal skiftast/skiftes
    "industri": ["løft", "frakt"],  # modulen skal løftast/fraktast/løftes/fraktes
}

# Ekstra ankernomen som bare skal telle i kombinasjon med et verb over (for
# generelle til å stå som frittstående STEM_KEYWORDS).
_EXTRA_ANCHOR_NOUNS: dict[str, list[str]] = {
    "havari_berging": ["fartøy", "skip", "båt", "tråler", "skute"],
    "industri": ["modul", "plattform"],
}

NORMALIZED_STEMS: dict[str, list[str]] = {
    cat: sorted({normalize_word(k) for k in words})
    for cat, words in STEM_KEYWORDS.items()
}

NORMALIZED_VERBS: dict[str, list[str]] = {
    cat: sorted({normalize_word(v) for v in verbs}) for cat, verbs in VERB_STEMS.items()
}

NORMALIZED_ANCHORS: dict[str, list[str]] = {
    cat: sorted(
        {normalize_word(w) for w in STEM_KEYWORDS.get(cat, []) + _EXTRA_ANCHOR_NOUNS.get(cat, [])}
    )
    for cat in VERB_STEMS
}

LOWER_PHRASES: dict[str, list[str]] = {
    cat: [p.lower() for p in phrases] for cat, phrases in PHRASE_KEYWORDS.items()
}


def _any_prefix_match(words: set[str], roots: list[str]) -> bool:
    return any(word.startswith(root) for word in words for root in roots)


def _any_substring_match(words: set[str], roots: list[str]) -> bool:
    # Brukes for ankerord: norske sammensetninger legger gjerne
    # bestemmerordet foran (fiskebåt, lastebåt), så roten ("båt") sitter ikke
    # nødvendigvis først i ordet slik den ville gjort med prefiksmatching.
    return any(root in word for word in words for root in roots)


def match_categories(text: str) -> list[str]:
    """Returnerer kategoriene en tekst (tittel + evt. sammendrag) treffer på."""
    words = normalize_text(text)
    lowered = text.lower()
    hits = []
    for cat in CATEGORIES:
        stem_hit = _any_prefix_match(words, NORMALIZED_STEMS[cat])
        phrase_hit = any(p in lowered for p in LOWER_PHRASES[cat])
        verb_hit = False
        if cat in VERB_STEMS:
            has_verb = _any_prefix_match(words, NORMALIZED_VERBS[cat])
            has_anchor = _any_substring_match(words, NORMALIZED_ANCHORS[cat])
            verb_hit = has_verb and has_anchor
        if stem_hit or phrase_hit or verb_hit:
            hits.append(cat)
    return hits
