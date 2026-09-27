"""Merge S2 + COCI (+OA when it lands) citer sets; resolve COCI DOIs via
Crossref; apply the keyword filter; diff against the existing citation map.
"""
import json
import re
import time
import urllib.request
import urllib.parse

HEAD = {"User-Agent": "algal-lab-cluster-audit/1.0 (mailto:audit@example.org)"}

KW = re.compile(r"mixtur|stochastic order|hazard rate|reversed hazard|likelihood.?ratio|"
                r"majoriz|outlier|order statisti|ageing|aging|residual life|mean residual|"
                r"proportional hazard|frailty|chain major", re.I)
NEG = re.compile(r"regression|neural|markov chain monte|survey|econometr", re.I)


def get(url, tries=5):
    req = urllib.request.Request(url, headers=HEAD)
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print("  retry %d %s: %s" % (a, url[:80], e), flush=True)
            time.sleep(3 + 3 * a)
    return None


def crossref_meta(doi):
    j = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if not j:
        return None
    it = j["message"]
    return {
        "doi": doi,
        "title": (it.get("title") or [""])[0],
        "venue": (it.get("container-title") or [""])[0],
        "year": (it.get("published-print") or it.get("published-online") or it.get("issued") or {}).get("date-parts", [[None]])[0][0],
        "authors": ["%s %s" % (a.get("given", ""), a.get("family", "")) for a in it.get("author", [])],
        "abstract": re.sub(r"<[^>]+>", " ", it.get("abstract") or ""),
        "src": "crossref",
    }


s2 = json.load(open("citers_s2.json"))
coci = json.load(open("citers_coci.json"))
try:
    oa = json.load(open("citers_oa.json"))
except FileNotFoundError:
    oa = {"edges": {}, "citers": {}}

# unified record keyed by lowercase DOI (S2) / DOI (COCI) / OA id
merged = {}  # key -> record
def key_of(rec):
    return (rec.get("doi") or rec.get("id") or rec.get("title","")[:40]).lower()

for pid, p in s2["citers"].items():
    ext = p.get("externalIds") or {}
    rec = {
        "doi": (ext.get("DOI") or "").lower(),
        "s2id": pid, "oaid": None,
        "title": p.get("title") or "",
        "abstract": p.get("abstract") or "",
        "year": p.get("year"),
        "venue": p.get("venue"),
        "authors": [a.get("name") for a in p.get("authors") or []],
        "oa_pdf": (p.get("openAccessPdf") or {}).get("url"),
        "cited_by": p.get("citationCount"),
        "handles": set(),
        "src": "s2",
    }
    merged[key_of(rec)] = rec

# S2 edges -> handle sets
s2_by_id = {}
for pid, p in s2["citers"].items():
    ext = p.get("externalIds") or {}
    s2_by_id[pid] = (ext.get("DOI") or "").lower() or pid
for key, pids in s2["edges"].items():
    for pid in pids:
        k = s2_by_id.get(pid)
        if k and k in merged:
            merged[k]["handles"].add(key)

# OA citers
for oid, w in oa.get("citers", {}).items():
    k = (w.get("doi") or oid).lower()
    if k in merged:
        merged[k]["oaid"] = oid
        if not merged[k]["abstract"]:
            merged[k]["abstract"] = w.get("abstract") or ""
        if not merged[k].get("oa_pdf"):
            merged[k]["oa_pdf"] = w.get("oa_url")
        merged[k]["locations"] = w.get("locations")
    else:
        merged[k] = {
            "doi": (w.get("doi") or "").lower(), "s2id": None, "oaid": oid,
            "title": w["title"], "abstract": w.get("abstract") or "",
            "year": w.get("year"), "venue": w.get("venue"),
            "authors": w.get("authors") or [], "oa_pdf": w.get("oa_url"),
            "locations": w.get("locations"), "cited_by": w.get("cited_by_count"),
            "handles": set(), "src": "oa",
        }
for key, oids in oa.get("edges", {}).items():
    for oid in oids:
        for k, rec in merged.items():
            if rec.get("oaid") == oid:
                rec["handles"].add(key)

# COCI DOIs -> crossref meta where not already merged
todo = []
for key, dois in coci.items():
    for d in dois:
        d = (d or "").lower()
        if not d:
            continue
        if d in merged:
            merged[d]["handles"].add(key)
        else:
            todo.append((key, d))
print("COCI-only DOIs to resolve:", len(todo))
resolved = {}
for key, d in sorted(set((k, d) for k, d in todo), key=lambda x: x[1]):
    if d in resolved:
        merged[d]["handles"].add(key)
        continue
    m = crossref_meta(d)
    if m:
        m["handles"] = {key}
        m["s2id"] = None; m["oaid"] = None; m["oa_pdf"] = None; m["cited_by"] = None
        merged[d] = m
        resolved[d] = m
    else:
        merged[d] = {"doi": d, "title": "?", "abstract": "", "year": None,
                     "venue": None, "authors": [], "handles": {key}, "src": "coci-unresolved"}
    time.sleep(0.4)

# keyword filter
kept, dropped = [], []
for k, rec in merged.items():
    text = (rec.get("title") or "") + " " + (rec.get("abstract") or "")
    rec["handles"] = sorted(rec["handles"])
    if KW.search(text) and not (NEG.search(text) and not KW.search(rec.get("title") or "")):
        kept.append(rec)
    else:
        dropped.append(rec)

kept.sort(key=lambda r: (r.get("year") or 0, r.get("title") or ""))
json.dump({"kept": kept, "dropped": dropped},
          open("citers_merged.json", "w"), indent=1)
print("\n== merged %d citers | kept %d | dropped %d ==\n" % (len(merged), len(kept), len(dropped)))
for r in kept:
    print("%s | %s | %s | %s | h=%s | %s" % (
        r.get("year"), r.get("doi") or "-", (r.get("venue") or "")[:38],
        r.get("title")[:68], ",".join(r["handles"]), (r.get("abstract") or "")[:0]))
print("\n== dropped ==")
for r in dropped:
    print("%s | %s | %s" % (r.get("year"), r.get("doi") or "-", r.get("title")[:80]))
