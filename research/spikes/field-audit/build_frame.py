"""Build the field-audit candidate frame (protocol.md, sections 1 and 2).

Queries the Semantic Scholar bulk search with the protocol's boolean rule and
re-applies the same rule locally to title and abstract. Semantic Scholar
withholds some publishers' abstracts, so a record whose abstract is withheld
cannot be re-checked; it is kept and flagged rather than dropped, since
dropping it would bias the frame against those publishers. Deduplicates by DOI
and writes:

  frame.json         canonical candidate records, sorted by key
  frame.sha256       SHA-256 of frame.json's bytes
  order.json         candidate keys in the hash-seeded screening order

The raw API response is kept outside Git (it contains publisher abstracts);
its SHA-256 is recorded in frame.json.

Eligibility screening and the known-cone exclusion happen later, in screening
order, and are recorded separately. Run from this directory:

  python3 build_frame.py
"""
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
HEAD = {"User-Agent": "algal-lab-field-audit/1.0"}
FIELDS = "title,abstract,year,venue,externalIds,isOpenAccess,openAccessPdf,publicationDate,publicationTypes"
DATES = "2010-01-01:2026-09-27"

PHRASES = ["stochastic comparison", "stochastic comparisons", "stochastic ordering",
           "stochastic orderings", "stochastic order", "stochastic orders"]
TOPICS = ["majorization", "heterogeneous", "mixture", "mixtures", "order statistic",
          "order statistics", "coherent system", "coherent systems", "series system",
          "series systems", "parallel system", "parallel systems"]


def quoted(term):
    return '"%s"' % term if " " in term else term


QUERY = "(%s) + (%s)" % (" | ".join(quoted(p) for p in PHRASES), " | ".join(quoted(t) for t in TOPICS))
PHRASE_RE = re.compile(r"\bstochastic (comparisons?|orderings?|orders?)\b", re.I)
TOPIC_RE = re.compile(r"\b(majori[sz]ation|heterogeneous|mixtures?|order statistics?|"
                      r"(coherent|series|parallel) systems?)\b", re.I)


def matches(record):
    text = " ".join(filter(None, [record.get("title"), record.get("abstract")]))
    return bool(PHRASE_RE.search(text) and TOPIC_RE.search(text))


def fetch(params, tries=8):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=60) as response:
                return json.loads(response.read().decode())
        except Exception as error:
            print("retry %d: %s" % (attempt, error), flush=True)
            time.sleep(5 + 10 * attempt)
    raise SystemExit("Semantic Scholar bulk search failed after %d attempts" % tries)


def key(record):
    ids = record.get("externalIds") or {}
    if ids.get("DOI"):
        return "doi:" + ids["DOI"].lower()
    if ids.get("ArXiv"):
        return "arxiv:" + ids["ArXiv"]
    return "s2:" + record["paperId"]


def main():
    params = {"query": QUERY, "fields": FIELDS, "publicationDateOrYear": DATES}
    raw, token, total = [], None, None
    while True:
        page = fetch(dict(params, **({"token": token} if token else {})))
        total = page.get("total", total)
        raw.extend(page.get("data") or [])
        print("fetched %d of %s" % (len(raw), total), flush=True)
        token = page.get("token")
        if not token:
            break
        time.sleep(2)

    raw_body = json.dumps(raw, ensure_ascii=False, sort_keys=True)
    raw_dir = "../context/runs/field-audit"
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "raw.json"), "w", encoding="utf-8") as out:
        out.write(raw_body)

    frame = {}
    for record in raw:
        if record.get("abstract"):
            if not matches(record):
                continue
            rule = "matched"
        else:
            rule = "matched" if matches(record) else "abstract_withheld"
        ids = record.get("externalIds") or {}
        pdf = record.get("openAccessPdf") or {}
        frame.setdefault(key(record), {
            "key": key(record),
            "s2": record["paperId"],
            "doi": ids.get("DOI"),
            "arxiv": ids.get("ArXiv"),
            "title": record.get("title"),
            "year": record.get("year"),
            "date": record.get("publicationDate"),
            "venue": record.get("venue"),
            "open_access": bool(record.get("isOpenAccess")),
            "oa_pdf": pdf.get("url") or None,
            "types": record.get("publicationTypes") or [],
            "local_rule": rule,
        })

    records = [frame[k] for k in sorted(frame)]
    body = json.dumps({"query": QUERY, "dates": DATES, "returned": len(raw),
                       "raw_sha256": hashlib.sha256(raw_body.encode("utf-8")).hexdigest(),
                       "records": records},
                      ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with open("frame.json", "w", encoding="utf-8") as out:
        out.write(body)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with open("frame.sha256", "w") as out:
        out.write(digest + "  frame.json\n")

    order = [r["key"] for r in records]
    random.Random(int(digest, 16)).shuffle(order)
    with open("order.json", "w") as out:
        json.dump({"seed_sha256": digest, "python": sys.version.split()[0], "order": order}, out, indent=1)
        out.write("\n")
    withheld = sum(r["local_rule"] == "abstract_withheld" for r in records)
    print("returned %d, kept %d (%d with abstract withheld), sha256 %s" % (len(raw), len(records), withheld, digest))


if __name__ == "__main__":
    main()
