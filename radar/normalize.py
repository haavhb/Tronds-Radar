"""Normaliserer norsk tekst (bokmål/nynorsk) for nøkkelordmatching.

Lokalaviser på Vestlandet skriver ofte nynorsk mens søkeordene i keywords.py
er bokmål. To systematiske skriftformforskjeller jevnes ut her:

- diftongen "øy" -> "ø" (grunnstøyting -> grunnstøting, grunnstøytt ->
  grunnstøtt)
- palataliseringen "gj" -> "g" (leggjast -> leggast, byggjast -> byggast)

Matching i keywords.py skjer deretter som prefiks ("startswith") mot korte
ordrøtter, f.eks. roten "løft" fanger både "løftast" (nynorsk) og "løftes"
(bokmål) uten at bøyningsendelsen ("-ast" vs "-es") trenger å strippes
eksplisitt.
"""

import re

_CHAR_SUBS = [
    ("øy", "ø"),
    ("gj", "g"),
]


def normalize_word(word: str) -> str:
    w = word.lower()
    for a, b in _CHAR_SUBS:
        w = w.replace(a, b)
    return w


_WORD_RE = re.compile(r"[a-zæøåôéèêA-ZÆØÅÔÉÈÊ]+")


def normalize_text(text: str) -> set[str]:
    """Returnerer settet av normaliserte ord i en tekst."""
    return {normalize_word(w) for w in _WORD_RE.findall(text)}
