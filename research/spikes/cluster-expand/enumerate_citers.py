"""Enumerate the full citer set of the defect handles via OpenAlex.

Run dir: research/spikes/context/runs/cluster-expand/ (gitignored).
Python: /Users/bg/Documents/algal-lab-worktrees/.venv-math/bin/python

Handles (task list; BHB2022 resolved = BKB2022 itself, see resolve_bhb.py —
the 'lemma source' paper the earlier audit called bhb2022 IS the PEIS paper;
its lemmas 2.4/2.5 restate BHM2015 Thm 2). Provenance handles added for
completeness: BHM2015 (true lemma source), HKFN2017, SAF2022.
"""
import json
import time
import urllib.request
import urllib.parse

API = "https://api.openalex.org"
HEAD = {"User-Agent": "algal-lab-cluster-audit/1.0 (mailto:audit@openalex.example)"}
SEL = "id,doi,title,publication_year,authorships,primary_location,open_access,best_oa_location,locations,cited_by_count,abstract_inverted_index"

HANDLES = {
    "HF2018":  "10.1007/s11749-018-0581-7",
    "NT2022":  "10.1080/03610926.2020.1788082",
    "BKB2022": "10.1017/S0269964820000467",
    "BKZ2021": "10.1016/j.spl.2021.109083",
    "SKF2026": "10.1002/asmb.70089",
    "SPBB2026": "10.1186/s13660-026-03450-7",
    # provenance/completeness handles
    "BHM2015": "10.1109/TR.2014.2354192",
    "HKFN2017": "10.1016/j.jmva.2017.06.003",
    "SAF2022": "10.1017/S0269964821000243",
}


def get(url, tries=6):
    req = urllib.request.Request(url, headers=HEAD)
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print("  retry %d: %s" % (a, e))
            time.sleep(4 + 4 * a)
    raise RuntimeError("failed: " + url)


def inv_to_abs(inv):
    if not inv:
        return ""
    pos = []
    for w, idxs in inv.items():
        for i in idxs:
            pos.append((i, w))
    return " ".join(w for _, w in sorted(pos))


def work_brief(w):
    locs = []
    for loc in w.get("locations") or []:
        pdf = loc.get("pdf_url")
        lp = loc.get("landing_page_url")
        if pdf or lp:
            locs.append({"pdf": pdf, "landing": lp,
                         "host": (loc.get("source") or {}).get("display_name")})
    return {
        "id": w["id"].rsplit("/", 1)[-1],
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": w.get("title") or "",
        "year": w.get("publication_year"),
        "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "oa": w.get("open_access", {}).get("is_oa"),
        "oa_url": (w.get("best_oa_location") or {}).get("pdf_url") or (w.get("best_oa_location") or {}).get("landing_page_url"),
        "locations": locs,
        "cited_by_count": w.get("cited_by_count"),
        "abstract": inv_to_abs(w.get("abstract_inverted_index")),
    }


def resolve_doi(doi):
    return get(API + "/works/" + urllib.parse.quote("doi:" + doi))


def citers(openalex_id):
    out = []
    cursor = "*"
    while True:
        url = API + "/works?" + urllib.parse.urlencode({
            "filter": "cites:%s" % openalex_id,
            "per-page": 200, "cursor": cursor, "select": SEL,
        })
        j = get(url)
        out.extend(work_brief(w) for w in j["results"])
        cursor = j["meta"].get("next_cursor")
        if not j["results"] or not cursor or len(out) >= j["meta"]["count"]:
            break
        time.sleep(1.0)
    return out


if __name__ == "__main__":
    handles = {}
    for key, doi in HANDLES.items():
        try:
            w = resolve_doi(doi)
            b = work_brief(w)
            handles[key] = b
            print("%-9s -> %s | citers=%s | %s" % (key, b["id"], b["cited_by_count"], b["title"][:70]))
            time.sleep(1.2)
        except Exception as e:
            print("%-9s FAILED: %s" % (key, e))

    all_citers, edges = {}, {}
    for key, h in handles.items():
        cs = citers(h["id"])
        edges[key] = [c["id"] for c in cs]
        for c in cs:
            all_citers.setdefault(c["id"], c)
        print("%-9s (%s): %d citers" % (key, h["id"], len(cs)))
        time.sleep(1.5)

    json.dump({"handles": handles, "edges": edges, "citers": all_citers},
              open("citers_raw.json", "w"), indent=1)
    print("\nunion: %d distinct citing works" % len(all_citers))
    print("saved citers_raw.json")
