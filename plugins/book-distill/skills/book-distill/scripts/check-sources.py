#!/usr/bin/env python3
"""Chapitres cités dans une fiche mais absents de ce qu'elle déclare avoir lu.

Usage : check-sources.py <fiche.md>

Cite = « (ch. N) », « (ch. N, M) », « (chapitre N) », « (chapitres N et M) », « (p. X, ch. N) ».
Déclaré = la ligne d'honnêteté de périmètre du gabarit :
  *Fiche fondée sur : …, N pages lues sur M (chapitres A : 1, 3, 5 à 7, B : 2, 8, C écartés : 9-11).*
Un chapitre A ou B peut être cité. Un chapitre C (écarté) ou absent de la ligne ne le peut pas :
soit on le lit et on le déclare, soit on retire la citation.

Sortie : une ligne par écart ; code 1 s'il y en a, 2 si la ligne de périmètre est introuvable.
"""
import re
import sys


def numbers(spec):
    """« 1, 3, 5 à 7 » ou « 9-11 » → {1, 3, 5, 6, 7} / {9, 10, 11}."""
    found = set()
    for part in re.split(r",|;|\bet\b|\band\b", spec):
        span = re.search(r"(\d+)\s*(?:à|-|–|to)\s*(\d+)", part)
        if span:
            found.update(range(int(span.group(1)), int(span.group(2)) + 1))
        else:
            found.update(int(n) for n in re.findall(r"\d+", part))
    return found


text = open(sys.argv[1], encoding="utf-8").read()

scope = re.search(r"Fiche fondée sur[^\n]*?\(([^)]*chapitres?[^)]*)\)", text)
if not scope:
    print("Ligne de périmètre introuvable (« Fiche fondée sur : … (chapitres A : …, B : …, C écartés : …) »)")
    sys.exit(2)

classes = {}
for label, spec in re.findall(r"\b([ABC])(?:\s+écartés?)?\s*:\s*([^:]*?)(?=,?\s*\b[ABC](?:\s+écartés?)?\s*:|$)", scope.group(1)):
    classes[label] = numbers(spec)
read = classes.get("A", set()) | classes.get("B", set())
skipped = classes.get("C", set())

body = text[: scope.start()]
cited = set()
for m in re.finditer(r"\((?:[^()]*?,\s*)?(?:ch\.|chapitres?)\s+([\d ,à\-–et]+)\)", body):
    cited.update(numbers(m.group(1)))

gaps = 0
for n in sorted(cited):
    if n in skipped:
        print(f"ch. {n} cité alors qu'il est déclaré écarté (C)")
        gaps += 1
    elif n not in read:
        print(f"ch. {n} cité mais absent des chapitres déclarés lus (A, B)")
        gaps += 1
print(f"{len(cited)} chapitres cités, {len(read)} déclarés lus, {gaps} écart(s)")
sys.exit(1 if gaps else 0)
