#!/usr/bin/env python3
"""Vérification anti-hallucination des références CIR.

Interroge des index bibliographiques publics et renvoie des métadonnées
AUTORITATIVES (titre, auteurs, revue, année, DOI). Le modèle recopie ces
champs ; il n'en invente JAMAIS. Une référence qui ne ressort d'aucun index
est suspecte d'invention -> à écarter.

Aucune dépendance externe (stdlib urllib). Nécessite un accès réseau.

Usage :
  verify-biblio.py search "distributed cache invalidation latency"  # OpenAlex : trouver des candidats
  verify-biblio.py doi 10.1016/j.jss.2021.110970                   # Crossref : vérifier qu'un DOI existe
  verify-biblio.py arxiv "distributed systems horizontal scalability"  # arXiv : chercher / vérifier
  verify-biblio.py hal "détection anomalies séries temporelles"    # HAL : littérature française
  verify-biblio.py check "Dupont" "systèmes distribués" 2021       # auteur+titre+année -> match ou NON TROUVÉ
  verify-biblio.py bibtex 10.1126/science.169.3946.635             # BibTeX canonique via DOI (citation propre)
  verify-biblio.py oa 10.1016/j.jss.2021.110970                    # Unpaywall : trouver le PDF en accès libre
  verify-biblio.py fetch 10.3390/app12126242 biblio                # télécharger le PDF OA (vrai PDF only) dans biblio/
  verify-biblio.py archive 10.1145/3358960.3375797 biblio          # article ferme : sauver metadonnees + abstract en .txt

Sortie : texte lisible + bloc « CITATION VÉRIFIÉE » prêt à coller.
Si rien n'est trouvé : « AUCUN RÉSULTAT — ne pas citer. »

RÈGLE : ne jamais recopier dans le dossier un champ qui ne vient pas d'une réponse
d'API ci-dessous. Toute source citée doit être rapatriée dans biblio/ (cmd fetch).
"""
import sys, json, urllib.parse, urllib.request
from xml.etree import ElementTree as ET

MAILTO = "cir@example.org"  # pool « poli » OpenAlex/Crossref ; remplacer par un vrai e-mail
UA = f"cir-biblio/1.0 (mailto:{MAILTO})"
# UA navigateur pour télécharger les PDF chez des éditeurs OA qui bloquent les bots (ex. MDPI -> 403)
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def _get(url, ua=UA, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _authors(names, max_n=6):
    names = [n for n in names if n]
    if not names:
        return "[auteurs non renvoyés]"
    if len(names) > max_n:
        return ", ".join(names[:max_n]) + " et al."
    return ", ".join(names)


def _citation_block(title, authors, venue, year, doi=None, url=None):
    print("\n--- CITATION VÉRIFIÉE (recopier tel quel) ---")
    print(f"Auteurs : {authors}")
    print(f"Titre   : {title}")
    print(f"Source  : {venue or '[non renvoyée]'}")
    print(f"Année   : {year or '[non renvoyée]'}")
    if doi:
        print(f"DOI     : https://doi.org/{doi}")
    if url:
        print(f"URL     : {url}")
    print("---------------------------------------------")


def search_openalex(query, n=5):
    q = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={q}&per-page={n}&mailto={MAILTO}"
    data = json.loads(_get(url))
    results = data.get("results", [])
    if not results:
        print("AUCUN RÉSULTAT — ne pas citer.")
        return
    print(f"{len(results)} candidat(s) OpenAlex pour : {query!r}\n")
    for i, w in enumerate(results, 1):
        title = w.get("display_name") or "[sans titre]"
        year = w.get("publication_year")
        authors = _authors([a["author"]["display_name"] for a in w.get("authorships", [])])
        src = (w.get("primary_location") or {}).get("source") or {}
        venue = src.get("display_name")
        doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
        cites = w.get("cited_by_count", 0)
        oa = (w.get("open_access") or {}).get("oa_url")
        print(f"[{i}] {title} ({year}) — {venue or 'venue ?'} — cité {cites}×")
        print(f"    {authors}")
        if doi:
            print(f"    DOI: {doi}")
        if oa:
            print(f"    PDF libre: {oa}")
        print()
    print("→ Vérifier le DOI de la (des) référence(s) retenue(s) avec : verify-biblio.py doi <DOI>")


def verify_doi(doi):
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    try:
        data = json.loads(_get(url))
    except Exception:
        print(f"DOI INTROUVABLE sur Crossref : {doi}\n→ NE PAS CITER (suspicion d'invention).")
        return
    m = data["message"]
    title = (m.get("title") or ["[sans titre]"])[0]
    authors = _authors([f"{a.get('given','')} {a.get('family','')}".strip() for a in m.get("author", [])])
    venue = (m.get("container-title") or [None])[0]
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        if k in m and m[k].get("date-parts"):
            year = m[k]["date-parts"][0][0]
            break
    print(f"DOI VALIDE ✓ : {doi}")
    _citation_block(title, authors, venue, year, doi=doi)


def search_arxiv(query, n=5):
    q = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{q}&max_results={n}"
    xml = _get(url)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml)
    entries = root.findall("a:entry", ns)
    if not entries:
        print("AUCUN RÉSULTAT arXiv — ne pas citer.")
        return
    print(f"{len(entries)} candidat(s) arXiv pour : {query!r}\n")
    for i, e in enumerate(entries, 1):
        title = " ".join((e.find("a:title", ns).text or "").split())
        year = (e.find("a:published", ns).text or "")[:4]
        authors = _authors([a.find("a:name", ns).text for a in e.findall("a:author", ns)])
        aid = (e.find("a:id", ns).text or "").strip()
        print(f"[{i}] {title} ({year})")
        print(f"    {authors}")
        print(f"    {aid}\n")


def search_hal(query, n=5):
    q = urllib.parse.quote(query)
    fl = "label_s,authFullName_s,producedDateY_i,doiId_s,uri_s"
    url = f"https://api.archives-ouvertes.fr/search/?q={q}&fl={fl}&rows={n}&wt=json"
    docs = json.loads(_get(url)).get("response", {}).get("docs", [])
    if not docs:
        print("AUCUN RÉSULTAT HAL — ne pas citer.")
        return
    print(f"{len(docs)} candidat(s) HAL pour : {query!r}\n")
    for i, d in enumerate(docs, 1):
        print(f"[{i}] {d.get('label_s','[sans label]')}")
        if d.get("authFullName_s"):
            print(f"    {_authors(d['authFullName_s'])}")
        if d.get("doiId_s"):
            print(f"    DOI: {d['doiId_s']}")
        if d.get("uri_s"):
            print(f"    {d['uri_s']}")
        print()


def check(author, title_words, year=None):
    """Anti-invention : la combinaison auteur+titre(+année) existe-t-elle vraiment ?"""
    query = f"{author} {title_words}"
    q = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={q}&per-page=5&mailto={MAILTO}"
    results = json.loads(_get(url)).get("results", [])
    tw = set(title_words.lower().split())
    for w in results:
        wt = (w.get("display_name") or "").lower()
        overlap = len(tw & set(wt.split())) / max(1, len(tw))
        yr_ok = (year is None) or (str(w.get("publication_year")) == str(year))
        if overlap >= 0.5 and yr_ok:
            doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
            print(f"MATCH PLAUSIBLE ✓ (recouvrement titre {overlap:.0%}, année {'OK' if yr_ok else 'différente'})")
            authors = _authors([a["author"]["display_name"] for a in w.get("authorships", [])])
            venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
            _citation_block(w.get("display_name"), authors, venue, w.get("publication_year"), doi=doi)
            return
    print(f"NON TROUVÉ pour « {author} / {title_words} / {year or '—'} »")
    print("→ Forte suspicion d'invention. NE PAS CITER sans source résolue.")


def bibtex(doi):
    """Citation canonique via DOI content negotiation (le LLM ne formate jamais de mémoire)."""
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://doi.org/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/x-bibtex"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(r.read().decode("utf-8", "replace").strip())
    except Exception:
        print(f"DOI INTROUVABLE : {doi}\n→ NE PAS CITER (suspicion d'invention).")


def unpaywall_oa(doi):
    """URL du PDF en accès libre (Unpaywall), ou None."""
    doi = doi.replace("https://doi.org/", "").strip()
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={MAILTO}"
    try:
        data = json.loads(_get(url))
    except Exception:
        return None
    loc = data.get("best_oa_location") or {}
    return loc.get("url_for_pdf") or loc.get("url")


def find_oa(doi):
    pdf = unpaywall_oa(doi)
    if pdf:
        print(f"PDF EN ACCÈS LIBRE : {pdf}")
        print(f"→ Rapatrier : verify-biblio.py fetch {doi} biblio")
    else:
        print("Pas de PDF en accès libre (Unpaywall).")
        print("→ Archiver l'abstract + la page DOI à la main dans biblio/, ou récupérer le PDF via accès institutionnel.")


def _slug(s, n=60):
    keep = "".join(c if c.isalnum() or c in " -_" else "-" for c in s)
    return "-".join(keep.split())[:n].strip("-")


def _openalex_abstract(doi):
    """Reconstruit l'abstract depuis l'index inversé OpenAlex (ou None)."""
    doi = doi.replace("https://doi.org/", "").strip()
    try:
        d = json.loads(_get(f"https://api.openalex.org/works/https://doi.org/{doi}?mailto={MAILTO}"))
    except Exception:
        return None, {}
    inv = d.get("abstract_inverted_index")
    abs = None
    if inv:
        pos = {}
        for word, idxs in inv.items():
            for i in idxs:
                pos[i] = word
        abs = " ".join(pos[i] for i in sorted(pos))
    meta = {
        "title": d.get("display_name"),
        "year": d.get("publication_year"),
        "venue": ((d.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "authors": ", ".join(a["author"]["display_name"] for a in d.get("authorships", [])),
    }
    return abs, meta


def fetch(doi, dest="biblio"):
    """Télécharge le PDF OA (vrai PDF seulement) dans dest/ et imprime la ligne d'index."""
    import os
    doi = doi.replace("https://doi.org/", "").strip()
    pdf = unpaywall_oa(doi)
    os.makedirs(dest, exist_ok=True)
    if not pdf:
        print(f"Pas de PDF OA pour {doi}. → article fermé : `archive {doi}` pour sauver abstract+métadonnées.")
        return
    fname = f"{_slug(doi.replace('/', '_'))}.pdf"
    path = os.path.join(dest, fname)
    try:
        raw = _get(pdf, ua=BROWSER_UA, accept="application/pdf,*/*")
    except Exception as e:
        print(f"Téléchargement bloqué ({e}). PDF annoncé : {pdf}\n→ récupérer à la main, ou `archive {doi}`.")
        return
    if raw[:4] != b"%PDF":
        print(f"⚠ Le contenu récupéré n'est PAS un PDF (probable page d'accès). Non sauvegardé.\n"
              f"→ article fermé : `archive {doi}`, ou récupérer le PDF via accès institutionnel ({pdf}).")
        return
    with open(path, "wb") as f:
        f.write(raw)
    print(f"✓ PDF {len(raw)} octets → {path}")
    print(f"Ligne d'index : | [réf] | {fname} | https://doi.org/{doi} | {pdf} | OA |")


def archive(doi, dest="biblio"):
    """Rapatrie un article FERMÉ : sauve métadonnées vérifiées + abstract en .txt."""
    import os
    doi = doi.replace("https://doi.org/", "").strip()
    abs_txt, meta = _openalex_abstract(doi)
    os.makedirs(dest, exist_ok=True)
    fname = f"{_slug(doi.replace('/', '_'))}.txt"
    path = os.path.join(dest, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Titre   : {meta.get('title','?')}\n")
        f.write(f"Auteurs : {meta.get('authors','?')}\n")
        f.write(f"Source  : {meta.get('venue','?')}\n")
        f.write(f"Année   : {meta.get('year','?')}\n")
        f.write(f"DOI     : https://doi.org/{doi}\n")
        f.write(f"Statut  : article fermé — métadonnées + abstract archivés (PDF via accès institutionnel)\n\n")
        f.write("ABSTRACT (source OpenAlex) :\n")
        f.write(abs_txt or "[abstract non disponible sur OpenAlex]\n")
    print(f"✓ archive → {path}")
    print(f"Ligne d'index : | [réf] | {fname} | https://doi.org/{doi} | https://doi.org/{doi} | FERMÉ |")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, arg = sys.argv[1], sys.argv[2]
    try:
        if cmd == "search":
            search_openalex(arg)
        elif cmd == "doi":
            verify_doi(arg)
        elif cmd == "arxiv":
            search_arxiv(arg)
        elif cmd == "hal":
            search_hal(arg)
        elif cmd == "check":
            check(arg, sys.argv[3] if len(sys.argv) > 3 else "", sys.argv[4] if len(sys.argv) > 4 else None)
        elif cmd == "bibtex":
            bibtex(arg)
        elif cmd == "oa":
            find_oa(arg)
        elif cmd == "fetch":
            fetch(arg, sys.argv[3] if len(sys.argv) > 3 else "biblio")
        elif cmd == "archive":
            archive(arg, sys.argv[3] if len(sys.argv) > 3 else "biblio")
        else:
            print(__doc__)
    except urllib.error.URLError as e:
        print(f"ERREUR RÉSEAU : {e}\n→ Si le shell est sandboxé, relancer avec accès réseau, "
              "ou interroger les mêmes API via WebFetch (URLs dans le code).")


if __name__ == "__main__":
    main()
