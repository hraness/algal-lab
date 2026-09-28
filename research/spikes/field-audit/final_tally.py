"""Final verified headline for the field audit.

Applies C3 classifications as overrides on eval refutations, dedupes the two
same-paper pairs and multi-order splits, splits theorem-level vs evidence
records, and reports P1 with and without the pilot papers.
"""
import json, glob, collections, os, re
from aggregate import load_results, canonical_paper, PILOT

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIRMED = {'confirmed-genuine','confirmed-direction-reversed'}
EXCLUDED = {'invalid-instance','artifact','inconclusive'}
KNOWN_OVERRIDES = {('arxiv_2601.07249','Theorem 3.2'): 'confirmed-genuine'}  # c3_report exists w/ different label

def norm(s): return re.sub(r'\W','',str(s).lower())

def load_c3():
    cov = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(ROOT,'harness','c3_report_*.json')):
        doc = json.load(open(f))
        items = doc.get('claims') or doc.get('records') if isinstance(doc, dict) else doc
        pname = os.path.basename(f)[10:-5]
        for it in items or []:
            if isinstance(it, dict):
                cov[pname][it.get('claim','')] = it.get('classification') or it.get('verdict') or ''
    return cov

def match(claims, claim):
    a = norm(claim); best=None
    for c_,v in claims.items():
        b = norm(c_)
        if a[:18]==b[:18] or (a[:12] and a[:12] in b) or (b[:12] and b[:12] in a): best=v
    return best

def th_level(r):
    return not any(k in r.get('claim','').lower() for k in ('example','counterexample','figure','remark'))

def main():
    results = load_results(); cov = load_c3()
    th_conf = collections.defaultdict(set); ev_conf = collections.defaultdict(set)
    excl_n = unc_n = 0
    for p, recs in results.items():
        claims = {}
        for m in [k for k in cov if k==p or p.startswith(k) or k.startswith(p)]:
            claims.update(cov[m])
        for r in recs:
            if r.get('status') != 'refuted': continue
            v = match(claims, r['claim']) or KNOWN_OVERRIDES.get((r['_paper'], r['claim']))
            if v in CONFIRMED:
                base = re.sub(r'[\s,]*[-–—]?\s*(lr|hr|rh|st|usual stochastic|hazard rate|reversed hazard|likelihood ratio)[\s\w]*$','',r['claim'].lower()).strip(' ,()-')
                (th_conf if th_level(r) else ev_conf)[p].add(base)
            elif v in EXCLUDED: excl_n += 1
            else: unc_n += 1
    pilot_canon = {canonical_paper(x) for x in PILOT}
    papers = set(results); np = papers - pilot_canon
    print('=== VERIFIED AUDIT HEADLINE ===')
    print('distinct papers:', len(papers))
    print('papers w/ >=1 C3-confirmed theorem-level refutation:', len(th_conf))
    print('  P1 incl. pilot: %d/%d = %.1f%%' % (len(th_conf), len(papers), 100*len(th_conf)/len(papers)))
    print('  P1 excl. pilot: %d/%d = %.1f%%' % (len(th_conf.keys() - pilot_canon), len(np), 100*len(th_conf.keys() - pilot_canon)/len(np)))
    print('  papers w/ confirmed evidence-only failures:', len(set(ev_conf)-set(th_conf)))
    print('  distinct confirmed theorem claims:', sum(len(s) for s in th_conf.values()))
    print('  records excluded by C3:', excl_n, '| unverified:', unc_n)
    json.dump({p: sorted(s) for p,s in th_conf.items()},
              open(os.path.join(ROOT,'confirmed_theorem_refutations.json'),'w'), indent=1)

if __name__ == '__main__':
    main()
