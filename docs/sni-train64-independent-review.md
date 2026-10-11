# Independent review: SNI train-only 64-task metadata pilot

**2026-10-11, local review; not a corpus admission or delivery approval.** Reviewed `AGENTS.md`, `docs/roadmap.md`, `docs/sni-train64-freeze.md`, `docs/sni-train64-receipt.md`, `docs/sni-corpus-intake.md`, and the SNI scripts, parsers and tests. No new task-body fetch, model call, test-task JSON access, PR operation, or paid request was made in this review.

## Separate findings

- **Correctness of the narrow stop:** The pinned index and independent index-audit copy are byte-identical (SHA-256 `2e54d1a3…`); 756 train / 119 test / 738 excluded task IDs. The first 64 bytewise-sorted train name/OID pairs reconstruct the frozen selection (SHA-256 `97cb7f38…`). Every numbered attempt has exactly one matching sidecar or failure record: 12 sidecars with only `task`, `blobOid`, `Source`, `Categories`, `Instance License`, and 52 failures (46 `blob-too-large`, six `invalid-JSON`). Plan and report both record $0. Thus at most 12 candidate groups can survive the frozen size-cap protocol, below 16, even before rights and aliases. This is an audit of the local records, **not** independent proof that the sidecars' values match the upstream bytes or that every upstream transport error was classified correctly: raw task bytes were not retained and deliberately were not refetched. The code checks Git blob OIDs before parsing; the ledger holds OIDs but does not cryptographically authenticate the extracted field values to a separate reviewer. The pre-access freeze chronology and all historical access/charges cannot be independently proved by this local ledger alone. No test-body URL is constructed by the reviewed fetch script; source code and sidecar schema do not establish the full historical access ledger.
- **Novelty / claim-to-source:** Independently fetched the pinned upstream `README.md` (SHA-256 `bd5c0768…`) and `splits/README.md` (SHA-256 `db3737ce…`), without task JSON. The upstream README says Apache-2.0 covers task data *except instances*, whose original-dataset terms are in each task's `Instance License`. The split README names train for modeling, test for reporting, and excluded tasks as an attempt to separate shared sources. This pilot applies an intake cap to that existing split; it neither establishes new task-family independence nor claims an algorithmic improvement. No selective-memory novelty or priority verdict is available; the primary-source comparisons requested by the roadmap for any eventual memory method remain a dependency.
- **Practical value / limits:** The stop prevents treating a sparse, rights-unreviewed development sample as a licensed source-disjoint comparison pool or spending on a premature six-arm study. It says nothing about the other 692 train names, accuracy, cost savings, consumer workload, or model intelligence. Rights and aliases, numerical quality/cost margins, full allowance, final holdout custodian and a task-family access history are still unestablished. The public SNI test partition is not a fresh model-pretraining holdout. No corpus group was admitted; no paid allowance was opened ($0 recorded).

## Validation and one bounded repair

Commands run from the repository root:

- The exact successful independent Python ledger and source-read commands are below. The first ledger invocation failed only because the reviewer expected 132 files instead of 131; the corrected version passed all index, split, selection, ledger-shape, outcome and reported-cost assertions. The initial source-read command had a Python syntax error before any request; the corrected command passed both upstream hashes. No attempt was fetched or retried.
- `bun test src/foundation/sni-intake.test.ts src/foundation/sni-train64.test.ts`: **7 pass, 0 fail**.
- `bun x tsc --noEmit`: pass.
- `bun run discovery doctor`: `ready: true`; `bun run discovery agenda cost-aware-research-memory`: `status: proposed`.
- `bun run check`: typecheck passed, suite began, `src/required-runner.test.ts` timed out (`Required preserves PR-only filtered skips with Bash only on slim`); host terminated the aggregate at **600,000 ms**, no final test status. A read-only `git status --short` initially timed out at 10,000 ms, then succeeded at 60,000 ms; no new tracked changes from that check appeared. **Aggregate remains unresolved**, not green; a separate PR-head `Required` has not run.

Repaired one stale statement in `docs/sni-corpus-intake.md`: the earlier 757-versus-756 estimate is now marked reconciled for the pinned revision, with a link to the later frozen-pilot record. The initial index receipt remains historically dated; no rights or source-group claims were upgraded. Relevant SNI scripts/tests and docs remain untracked in the shared working tree, alongside unrelated host-comparison changes; nothing was committed, pushed or merged.

**Durable blocker / next dependency:** Keep this frozen 64-task pilot stopped. Do not fetch its failed blobs again, alter its cap/selection, read public test-task bodies or run a paid comparison to evade the stop. The integration owner must resolve the aggregate check on the exact eventual source tree, obtain independent source/rights review only for a *new pre-access protocol* if choosing a different development corpus/sample, freeze a genuinely independent holdout and numerical protocol before any comparison, and wait for PR-head `Required` plus independent review before delivery. The owner-decision corpus/holdout question in `docs/cost-aware-memory-gate.md` remains open; owner unavailable until 2026-11-05.

## Exact successful independent commands

No shell script or output artifact was created by these read-only commands:

```sh
python3 -c 'from pathlib import Path
import hashlib,json,collections
p=Path("runs/sni-train64-20261011-01"); idx=Path("runs/sni-index-20261008-01/task-blob-oids.tsv").read_bytes(); fresh=Path("runs/sni-index-audit-20261011-01/task-blob-oids.tsv").read_bytes(); sel=(p/"selection.tsv").read_bytes(); H=lambda b:hashlib.sha256(b).hexdigest(); assert idx==fresh and H(idx)=="2e54d1a3c0ff5887ffbaf5fabdeafab5cdadd97e674f167de7359b9304185f38"; assert H(sel)=="97cb7f38b55869de58e4667f28458d2c1d15799211bfdb9e25d795b9444f0728"; rows=[tuple(x.split("\t")) for x in idx.decode().splitlines()]; counts=collections.Counter(r[0] for r in rows); assert counts=={"train":756,"test":119,"excluded":738}; chosen=sorted((r for r in rows if r[0]=="train"),key=lambda r:r[1])[:64]; assert sel=="".join("\t".join(r)+"\n" for r in chosen).encode(); plan=json.loads((p/"plan.json").read_text()); report=json.loads((p/"report.json").read_text()); assert plan["testNamesSha256"]==H(("\n".join(sorted(r[1] for r in rows if r[0]=="test"))+"\n").encode()); assert plan["paidUsd"]==report["paidUsd"]==0 and plan["count"]==plan["maxFetches"]==64 and plan["fetchLimitBytes"]==1000000; failures=collections.Counter(); sides=0
for i,(_,task,oid) in enumerate(chosen,1):
    stem=f"{i:02d}"; a=json.loads((p/f"{stem}.attempt.json").read_text()); assert a=={"task":task,"blobOid":oid,"status":"started"}; f=p/f"{stem}.failure.json"; s=p/f"{stem}.sidecar.json"; assert f.exists()!=s.exists()
    if f.exists():
        x=json.loads(f.read_text()); assert x["task"]==task and x["blobOid"]==oid and set(x)=={"task","blobOid","code","disposition"}; failures[x["code"]]+=1
    else:
        x=json.loads(s.read_text()); assert x["task"]==task and x["blobOid"]==oid and set(x)=={"task","blobOid","Source","Categories","Instance License"}; sides+=1
assert sides==report["statuses"]["extracted"]==12 and sum(failures.values())==report["statuses"]["failed"]==52
assert set(failures)=={"blob-too-large","invalid-JSON"} and failures["blob-too-large"]==46 and failures["invalid-JSON"]==6
assert len(list(p.iterdir()))==3+2*64
print("index/selection match; splits",dict(counts),"attempts 64; sidecars",sides,"failures",dict(failures),"cost $0 (reported); no extra files")'
```

Output: `index/selection match; splits {'train': 756, 'test': 119, 'excluded': 738} attempts 64; sidecars 12 failures {'blob-too-large': 46, 'invalid-JSON': 6} cost $0 (reported); no extra files`.

```sh
python3 -c 'import urllib.request,hashlib
base="https://raw.githubusercontent.com/allenai/natural-instructions/55a365637381ce7f3748fa2eac7aef1a113bbb82/"
for path,expected in [("README.md","bd5c0768d317f0184c00afd3233d166672aa63a6fee52fa368f3aa117111ccd7"),("splits/README.md","db3737ce9310717e3ef6ec6a787b816e8e9249fbbd7c200db365cbbb14ea018c")]:
 r=urllib.request.urlopen(urllib.request.Request(base+path,headers={"User-Agent":"algal-independent-source-review"}),timeout=20); b=r.read(200001); assert len(b)<=200000 and hashlib.sha256(b).hexdigest()==expected; text=b.decode(); print(path,"sha256 verified"); print("\n".join(line[:250] for line in text.splitlines() if any(s in line.lower() for s in ["license","train","test","exclude","instance"]))[:3000])'
```

Output: both pinned README digests verified; license and split-role passages printed. No task blobs requested.
