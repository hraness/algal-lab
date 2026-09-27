"""Screen frame candidates in the frozen order (protocol.md, section 2).

For each candidate, in order.json order:
  1. excluded if its DOI or arXiv id appears in a prior audit memo
     (prior_audit_ids.json);
  2. not retrievable unless it has an arXiv id or a Semantic Scholar
     open-access PDF link, and the download yields a PDF with text;
  3. otherwise the text is scanned for theorem-like statements (Theorem,
     Proposition, Corollary) that name a stochastic order, falling back to any
     passage that names one; the snippets go to the screener, whose manual
     review decides eligibility.

Stops once `--target` candidates have at least one flagged statement. PDFs and
text go to ../context/runs/field-audit/ (outside Git). Writes
screening_candidates.json; the screener's decisions go in screening.json.

  python3 screen.py --target 130
"""
import argparse
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request

RUNS = "../context/runs/field-audit"
HEAD = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 algal-lab-field-audit/1.0", "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8"}
PDF_META = re.compile(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', re.I)

ORDER_PATTERNS = [
    r"usual stochastic order", r"stochastic(ally)? (smaller|larger|greater|ordered)",
    r"hazard rate order", r"reversed hazard rate order", r"likelihood ratio order",
    r"dispersive order", r"star order", r"star-shaped order", r"lorenz order",
    r"convex transform order", r"ageing faster", r"aging faster", r"mean residual life order",
    r"increasing convex order", r"right spread order",
    r"[≤≥⩽⩾<>]\s?_?\{?\s?(st|hr|rh|lr|disp|icx|icv|mrl|c|∗|\*|Lorenz|RS)\b",
]
ORDER_RE = re.compile("|".join(ORDER_PATTERNS), re.I)
STATEMENT_RE = re.compile(r"(?m)^\s*(Theorem|Proposition|Corollary)\s+\d+(\.\d+)*\b")


def safe(key):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", key)


def fetch(url):
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read(), response.geturl()


def download(urls, path):
    """Try each URL; follow a landing page's citation_pdf_url meta tag once."""
    errors = []
    for url in urls:
        try:
            data, final = fetch(url)
            if not data.startswith(b"%PDF"):
                match = PDF_META.search(data[:200000].decode("utf-8", "replace"))
                if not match:
                    raise ValueError("landing page without citation_pdf_url")
                data, final = fetch(urllib.parse.urljoin(final, match.group(1)))
            if not data.startswith(b"%PDF"):
                raise ValueError("not a PDF (%d bytes)" % len(data))
            with open(path, "wb") as out:
                out.write(data)
            return url
        except Exception as error:
            errors.append("%s: %s" % (url[:80], str(error)[:80]))
    raise ValueError(" | ".join(errors))


def candidate_urls(record):
    urls = []
    if record["arxiv"]:
        urls.append("https://arxiv.org/pdf/%s" % record["arxiv"])
    if record["oa_pdf"]:
        urls.append(record["oa_pdf"])
    doi = record["doi"] or ""
    if record["oa_pdf"] and doi.lower().startswith(("10.1007/", "10.1186/")):
        urls.append("https://link.springer.com/content/pdf/%s.pdf" % doi)
    return urls


def statements(text):
    """Theorem-like statements that name an order; failing that, passages that do.

    Unnumbered theorems ("as shown in the following theorem") are common in this
    literature, so any passage naming an order is flagged for manual review.
    """
    found = []
    starts = [m.start() for m in STATEMENT_RE.finditer(text)]
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else start + 1200
        block = " ".join(text[start:min(end, start + 1200)].split())
        head = block[:600]
        if ORDER_RE.search(head):
            found.append(head)
    if not found:
        for match in list(ORDER_RE.finditer(text))[:4]:
            found.append("[passage] " + " ".join(text[max(0, match.start() - 250):match.end() + 350].split()))
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=130)
    args = parser.parse_args()

    frame = {r["key"]: r for r in json.load(open("frame.json"))["records"]}
    order = json.load(open("order.json"))["order"]
    prior = json.load(open("prior_audit_ids.json"))
    prior_dois, prior_arxiv = set(prior["dois"]), set(prior["arxiv"])
    os.makedirs(os.path.join(RUNS, "pdf"), exist_ok=True)

    out_path = "screening_candidates.json"
    done = {c["key"]: c for c in json.load(open(out_path))["candidates"]} if os.path.exists(out_path) else {}
    candidates, flagged = [], 0
    for position, key in enumerate(order):
        if flagged >= args.target:
            break
        if key in done:
            candidate = done[key]
        else:
            record = frame[key]
            candidate = {"position": position, "key": key, "title": record["title"],
                         "year": record["year"], "venue": record["venue"]}
            if (record["doi"] and record["doi"].lower() in prior_dois) or (record["arxiv"] and record["arxiv"] in prior_arxiv):
                candidate["status"] = "excluded_prior_audit"
            else:
                urls = candidate_urls(record)
                if not urls:
                    candidate["status"] = "no_open_full_text"
                else:
                    pdf = os.path.join(RUNS, "pdf", safe(key) + ".pdf")
                    txt = pdf[:-4] + ".txt"
                    try:
                        if not os.path.exists(pdf):
                            candidate["source_url"] = download(urls, pdf)
                            time.sleep(3)
                        subprocess.run(["pdftotext", "-layout", pdf, txt], check=True, timeout=120)
                        text = open(txt, encoding="utf-8", errors="replace").read()
                        if len(text.strip()) < 2000:
                            candidate["status"] = "no_text_layer"
                        else:
                            found = statements(text)
                            candidate["status"] = "flagged" if found else "no_order_statement_found"
                            candidate["statements"] = found[:6]
                    except Exception as error:
                        candidate["status"] = "download_failed"
                        candidate["error"] = str(error)[:200]
            print("%4d %-26s %s" % (position, candidate["status"], (candidate["title"] or "")[:60]), flush=True)
        candidates.append(candidate)
        flagged += candidate["status"] == "flagged"

    with open(out_path, "w", encoding="utf-8") as out:
        json.dump({"target": args.target, "candidates": candidates}, out, ensure_ascii=False, indent=1)
        out.write("\n")
    counts = {}
    for c in candidates:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    print("screened %d candidates: %s" % (len(candidates), counts))


if __name__ == "__main__":
    main()
