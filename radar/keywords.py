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
        # "vraket forslaget"). Fanges i stedet opp via GATED_TERMS lenger
        # ned, som krever et fartøysord i samme tekst.
        #
        # NB: "nødhavn" er også bevisst utelatt herfra. Ordet brukes både
        # om fartøy i reell nød OG om en tilbakevendende lokalsak der
        # båteiere ligger fast forankret i en nødhavn i strid med
        # kommunen (en forvaltningssak, ikke en nødssituasjon til sjøs).
        # Fanges opp via GATED_TERMS, som krever et faktisk nødsignal-ord
        # i samme tekst.
        "grunnstøt", "grunnstøyt", "forlis", "forlist", "kantr",
        "slepebåt", "synkeferdig", "havarikommisjon",
    ],
    "infrastruktur": [
        # NB: "kai" og "molo" står IKKE her, men i SUBSTRING_STEMS under -
        # norske sammensetninger legger bestemmerordet foran (betongkai,
        # fiskerikai, steinmolo), så prefiksmatch alene ville bommet på
        # disse. Alt som prefiksmatcher "kai"/"molo" fanges uansett opp av
        # substring-matchen (den er en overmengde), så egne oppføringer for
        # f.eks. "ferjekai"/"kaielement" er unødvendige her.
        "brufundament",
        "sjøledning", "sjøkabel", "sjøkabling", "kabellegging",
        "rørledning",
        "spunt", "peling", "pelearbeid",
        "bruelement", "brurehabilitering", "brobygging", "broprosjekt",
        "brokonstruksjon",
        "havneutbygging", "havneutvikling", "havneprosjekt", "havneanlegg",
        "sjøfrontutvikling", "fiskerihavn", "mudring", "flytebrygge",
        "bølgebryter", "pontong", "sjøentreprise",
        # NB: bare "bro"/"bru" alene er utelatt - kolliderer med
        # "brud"/"brudgom" (bryllup) siden begge starter på "bru". Fanges
        # opp via PHRASE_KEYWORDS kombinert med et bygge-/rive-verb i
        # stedet, se under.
    ],
    "oppdrett": [
        # NB: "oppdrett" og "havbruk" er bevisst utelatt som frittstående
        # stammer - begge er for generelle (matcher praktisk talt alt fra
        # bransjepressen, inkl. ren finansnyheter), og fanges likevel opp
        # via mer spesifikke substantiv og fraser under, eller (for
        # havbruk) via GATED_TERMS/PHRASE_KEYWORDS kombinert med et
        # bransjesignal (kontrakt, investering osv.).
        "merd", "fôrflåte", "forflåte", "fortøy", "akvakultur",
        "slaktemerd", "notpose",
        "betongflåte", "arbeidsflåte", "serviceflåte", "oppdrettsflåte",
        "flytekrage", "settefisk", "slakteri", "ankerhåndter",
        "ankerinstallasjon", "oppdrettsutstyr", "betongelement",
    ],
    "industri": [
        "riving", "rivast", "rives", "revet",
        "decommission", "nedstenging", "modultransport",
        "tungløft", "tungloft", "smelteverk", "prosessanlegg",
        "tungtransformator", "industribygg", "breakbulk", "kranlekter",
        "sjøløft", "industrimodul", "fabrikkmoduler", "industrimoduler",
        "modulbygg", "hydrogenfabrikk", "batterifabrikk", "ammoniakkterminal",
        "transformatorstasjon", "offshorebase", "prosjektlast",
        "prosjektlogistikk", "industriprosjekt", "industripark",
        "karbonfangst", "havvind", "industrikai", "fabrikkutvidelse",
        "hydrogenanlegg", "ammoniakkanlegg", "produksjonslinje",
        "stålkonstruksjon", "stålkonstruksjoner", "maskinflytting",
        "spesialtransport", "sjøtransport", "tunggods", "skipslast",
        "lektertransport", "havneterminal", "oljebase",
        # NB: "transformator", "tank", "silo", "terminal", "lager",
        # "kraftverk" osv. er bevisst utelatt som frittstående stammer - for
        # tvetydige alene ("tank" prefiksmatcher "tanke"/"tenke", "terminal"
        # kan være buss-/flyterminal, "lager" er et helt vanlig ord).
        # Fanges opp via PHRASE_KEYWORDS kombinert med et transport-/
        # løfteverb i stedet, se under.
    ],
}

# Flerords-uttrykk. Matches som "alle betydningsbærende ord finnes et sted i
# teksten" (rekkefølge/nærhet spiller ingen rolle, og småord som "av"/"til"
# ignoreres) - IKKE som eksakt sammenhengende delstreng. Dette gjør at f.eks.
# "transport av merder" også fanger opp "transporterer oppdrettsmerder til
# lokaliteten", ikke bare den eksakte ordrekkefølgen. Brukes for ord som er
# for generelle til å stå alene (transport, levering, kontrakt, investering
# osv.), forankret til et spesifikt substantiv fra samme setning.
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
        # "marina"/"bro"/"bru" er for tvetydige alene (marina - se
        # nødhavn-saken over; bro/bru - kolliderer med "brud"), krever et
        # bygge-/rive-/prosjekt-verb i samme tekst.
        "bygg marina", "etabler marina", "prosjekter marina",
        "anlegg marina",
        "bygg bro", "bygg bru", "prosjekter bro", "prosjekter bru",
        "riv bro", "riv bru", "rehabiliter bro", "rehabiliter bru",
        "milliardprosjekt havn", "betong sjøveien",
    ],
    "oppdrett": [
        "ny lokalitet", "lokalitet for oppdrett", "utvidelse av lokalitet",
        "oppdrettskonsesjon", "konsesjon for oppdrett", "fôrflåte skal",
        "merder skal", "flytte anlegget", "skifte merder",
        # Generiske ord (etabler/utvid/kjøp/kontrakt/invester osv.) er for
        # brede alene, men trygge kombinert med et bransjeord.
        "etabler oppdrettsanlegg", "utvid oppdrettsanlegg",
        "flytt oppdrettsanlegg", "demonter oppdrettsanlegg",
        "oppgrader lokalitet", "service oppdrettsanlegg",
        "sjøsett flåte", "løft flåte",
        "kjøp oppdrettsanlegg", "kjøp oppdrettslokalitet",
        "kjøp havbruksselskap", "selg oppdrettsanlegg",
        "invester oppdrett", "invester havbruk",
        "kontrakt oppdrett", "kontrakt havbruk",
        "tildel kontrakt oppdrett", "tildel kontrakt havbruk",
        "utbygging havbruk", "søk lokalitet", "søk tillatelse oppdrett",
        "nytt konsesjonsområde", "milliardinvester havbruk",
        "havbruk sats", "avtale oppdrett", "avtale havbruk",
        "lever oppdrett", "lever havbruk",
        "landbasert oppdrett", "offshore havbruk", "offshore oppdrett",
        "eksponert oppdrett", "havbruk havs",
    ],
    "industri": [
        "modul skal fraktes", "modul skal løftes", "plattform skal fjernes",
        "fabrikk skal rives", "rive fabrikken", "tungt utstyr skal fraktes",
        "sjøtransport av modul",
        # Generiske substantiv (transformator/tank/silo/stål/betong) er for
        # brede alene, men trygge kombinert med et transport-/løfteverb.
        "transport transformator", "transport silo",
        # NB: "tank" er bevisst utelatt her - prefiksmatcher "tanker"/"tanke"
        # (tanker om noe), som ville gitt falske treff sammen med "transport".
        "transport stål", "transport betong", "løft maskineri",
        "løft betongelement", "frakt betongelement",
        # Fabrikk-/industriparkutbygging - trenger et bygge-/kjøpeverb, ikke
        # bare "ny fabrikk" (som ville kollapse til bare "fabrikk" siden "ny"
        # er et fjernet småord).
        "kjøp fabrikk", "bygg fabrikk", "utvid fabrikk",
        "milliardinvester industri", "kontrakt industri",
        # Hyphenerte forkortelser ("LNG-anlegg", "CCS-anlegg", "EPC-kontrakt")
        # tokeniseres som to separate ord siden normalize_text ikke regner
        # bindestrek som en del av ordet - bag-match fanger dem likevel opp.
        "lng anlegg", "ccs anlegg", "epc kontrakt",
        "plugging fjerning",
    ],
}

# Uregelmessige nynorskformer som normaliseringsreglene ikke fanger
# automatisk (listes opp som ekstra stammer per kategori).
_EXTRA_NYNORSK_STEMS = {
    "oppdrett": ["flytj"],  # flytjast (nynorsk) vs flyttes (bokmål)
}
for _cat, _extra in _EXTRA_NYNORSK_STEMS.items():
    STEM_KEYWORDS[_cat].extend(_extra)

# Ord/stammer som er for generiske eller tvetydige til å telle alene (f.eks.
# "løftes"/"legges"/"skiftes" er vanlige ord i alle slags sammenhenger, og
# "nødhavn" brukes også om en forvaltningstvist uten reell nødssituasjon),
# men som er sterke signaler når de opptrer sammen med et forankrende ord i
# samme tekst. Hver regel har sitt eget sett med ekstra ankerord, siden ulike
# ord trenger ulik kontekst for å telle som reelt treff (f.eks. trenger ikke
# "vrak" samme anker som "nødhavn" - et fartøysord holder ikke for nødhavn,
# siden båteier-tvisten også handler om båter).
GATED_TERMS: list[dict] = [
    {
        # vraket (skipsvrak) vs. vraket (forkastet) - krever fartøysord.
        "category": "havari_berging",
        "stems": ["vrak"],
        "extra_anchors": ["fartøy", "skip", "båt", "tråler", "skute"],
    },
    {
        # nødhavn (fartøy i reell nød) vs. nødhavn (forvaltningstvist om
        # båter som ligger fast forankret) - krever et faktisk
        # nødsignal-ord, ikke bare et fartøysord.
        "category": "havari_berging",
        "stems": ["nødhavn"],
        "extra_anchors": [
            "brann", "lekkasje", "kollisjon", "kolliderte", "kolliderer",
            "drivende", "assistanse", "motorstopp", "nødstedt",
        ],
    },
    {
        "category": "infrastruktur",
        "stems": ["legg"],  # sjøkabelen skal leggjast/legges
        "extra_anchors": [],
    },
    {
        "category": "oppdrett",
        "stems": ["skift"],  # merdene skal skiftast/skiftes
        "extra_anchors": [],
    },
    {
        "category": "industri",
        "stems": ["løft", "frakt"],  # modulen skal løftast/fraktast/løftes/fraktes
        "extra_anchors": ["modul", "plattform"],
    },
]

# Stammer som skal matches som substring i ordet (ikke bare prefiks), for
# sammensetninger der bestemmerordet står bakerst i stedet for først
# (betongkai, fiskerikai, steinmolo).
SUBSTRING_STEMS: dict[str, list[str]] = {
    "infrastruktur": ["kai", "molo"],
}

NORMALIZED_STEMS: dict[str, list[str]] = {
    cat: sorted({normalize_word(k) for k in words})
    for cat, words in STEM_KEYWORDS.items()
}

NORMALIZED_SUBSTRING_STEMS: dict[str, list[str]] = {
    cat: sorted({normalize_word(k) for k in words})
    for cat, words in SUBSTRING_STEMS.items()
}

# Småord som ikke bærer betydning og derfor ikke skal kreves som eget treff
# når en flerords-frase brytes opp i enkeltord.
_STOPWORDS = {
    "av", "til", "for", "i", "med", "på", "som", "og", "en", "ei", "et",
    "den", "det", "de", "sin", "sitt", "sine", "skal", "blir", "ble", "er",
    "har", "vil", "kan", "over", "under", "ved", "fra", "mot", "om",
    "ny", "nytt", "nye", "sitt", "seg",
}


def _phrase_to_stems(phrase: str) -> list[str]:
    return [normalize_word(w) for w in phrase.lower().split() if w not in _STOPWORDS]


# Hver frase er nå en liste av normaliserte ord-stammer (småord fjernet) som
# ALLE må finnes et sted i teksten (se _bag_match), ikke en sammenhengende
# delstreng.
NORMALIZED_PHRASES: dict[str, list[list[str]]] = {
    cat: [_phrase_to_stems(p) for p in phrases] for cat, phrases in PHRASE_KEYWORDS.items()
}

# Ankeret for en gated-regel er kategoriens egne stammer (ordet skal telle
# hvis det opptrer sammen med ETHVERT annet signal fra samme kategori) pluss
# ev. ekstra ankerord spesifikke for akkurat den regelen.
_NORMALIZED_GATES: list[dict] = [
    {
        "category": rule["category"],
        "stems": sorted({normalize_word(s) for s in rule["stems"]}),
        "anchors": sorted(
            {
                normalize_word(a)
                for a in STEM_KEYWORDS.get(rule["category"], []) + rule["extra_anchors"]
            }
        ),
    }
    for rule in GATED_TERMS
]


def _any_prefix_match(words: set[str], roots: list[str]) -> bool:
    return any(word.startswith(root) for word in words for root in roots)


def _any_substring_match(words: set[str], roots: list[str]) -> bool:
    # Brukes for ankerord: norske sammensetninger legger gjerne
    # bestemmerordet foran (fiskebåt, lastebåt), så roten ("båt") sitter ikke
    # nødvendigvis først i ordet slik den ville gjort med prefiksmatching.
    return any(root in word for word in words for root in roots)


def _bag_match(words: set[str], stems: list[str]) -> bool:
    # Alle stammene i frasen må finnes et sted i teksten (ikke nødvendigvis
    # etter hverandre) - se NORMALIZED_PHRASES over for hvorfor.
    return all(_any_prefix_match(words, [stem]) for stem in stems)


def match_categories(text: str) -> list[str]:
    """Returnerer kategoriene en tekst (tittel + evt. sammendrag) treffer på."""
    words = normalize_text(text)
    hits = []
    for cat in CATEGORIES:
        stem_hit = _any_prefix_match(words, NORMALIZED_STEMS[cat]) or _any_substring_match(
            words, NORMALIZED_SUBSTRING_STEMS.get(cat, [])
        )
        phrase_hit = any(_bag_match(words, stems) for stems in NORMALIZED_PHRASES[cat])
        gated_hit = any(
            gate["category"] == cat
            and _any_prefix_match(words, gate["stems"])
            and _any_substring_match(words, gate["anchors"])
            for gate in _NORMALIZED_GATES
        )
        if stem_hit or phrase_hit or gated_hit:
            hits.append(cat)
    return hits
