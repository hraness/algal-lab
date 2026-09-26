"""Enumerate citers via Semantic Scholar Graph API + OpenCitations COCI.
Fallback because api.openalex.org is 429-throttled on this egress.

Handle OA IDs already resolved:
  HF2018  W2794786652   doi 10.1007/s11749-018-0581-7
  NT2022  (resolve)     doi 10.1080/03610926.2020.1788082
  BKB2022 W3086585527   doi 10.1017/S0269964820000467
  BKZ2021 W3135013245   doi 10.1016/j.spl.2021.109083
  SKF2026 W7151946601   doi 10.1002/asmb.70089
  SPBB2026 W7131069508  doi 10.1186/s13660-026-03450-7
  BHM2015               doi 10.1109/TR.2014.2354192
  HKFN2017              doi 10.1016/j.jmva.2017.06.003
  SAF2022               doi 10.1017/S0269964821000243
"""
import json
import time
import urllib.request
import urllib.parse

HEAD = {"User-Agent": "algal-lab-cluster-audit/1.0"}

HANDLES = {
    "HF2018":  "10.1007/s11749-018-0581-7",
    "NT2022":  "10.1080/03610926.2020.1788082",
    "BKB2022": "10.1017/S0269964820000467",
    "BKZ2021": "10.1016/j.spl.2021.109083",
    "SKF2026": "10.1002/asmb.70089",
    "SPBB2026": "10.1186/s13660-026-03450-7",
    "BHM2015": "10.1109/TR.2014.2354192",
    "HKFN2017": "10.1016/j.jmva.2017.06.003",
    "SAF2022": "10.1017/S0269964821000243",
}
FIELDS = "title,abstract,authors,venue,year,externalIds,openAccessPdf,citationCount,publicationTypes"


def get(url, tries=6, quiet=False):
    req = urllib.request.Request(url, headers=HEAD)
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if not quiet:
                print("  retry %d: %s" % (a, e), flush=True)
            time.sleep(5 + 5 * a)
    return None


def s2_citations(doi):
    """All citing papers via S2, paginated by offset (limit<=100)."""
    out = []
    offset = 0
    while True:
        url = ("https://api.semanticscholar.org/graph/v1/paper/DOI:%s/citations?"
               % urllib.parse.quote(doi)) + urllib.parse.urlencode({
            "fields": "citingPaper." + ",citingPaper.".join(FIELDS.split(",")),
            "limit": 100, "offset": offset,
        })
        j = get(url)
        if j is None:
            return out
        for row in j.get("data", []):
            p = row.get("citingPaper") or {}
            if p.get("paperId"):
                out.append(p)
        if len(j.get("data", [])) < 100:
            break
        offset += 100
        time.sleep(1.2)
    return out


def coci_citations(doi):
    j = get("https://opencitations.net/index/api/v1/citations/" + urllib.parse.quote(doi))
    if not j:
        return []
    return [r.get("citing") for r in j if r.get("citing")]


if __name__ == "__main__":
    s2_all, s2_edges = {}, {}
    for key, doi in HANDLES.items():
        ps = s2_citations(doi)
        s2_edges[key] = [p["paperId"] for p in ps]
        for p in ps:
            p["_handle_doi"] = doi
            s2_all.setdefault(p["paperId"], p)
        print("S2  %-9s %s: %d citers" % (key, doi, len(ps)), flush=True)
        time.sleep(2.5)

    json.dump({"edges": s2_edges, "citers": s2_all}, open("citers_s2.json", "w"), indent=1)
    print("S2 union:", len(s2_all))

    # COCI complement (DOI-level edges only)
    coci = {}
    for key, doi in HANDLES.items():
        cs = coci_citations(doi)
        coci[key] = cs
        print("COCI %-9s %s: %d citers" % (key, doi, len(cs)), flush=True)
        time.sleep(1.5)
    json.dump(coci, open("citers_coci.json", "w"), indent=1)
