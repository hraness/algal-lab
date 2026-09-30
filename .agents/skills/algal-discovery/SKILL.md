---
name: algal-discovery
description: Run or resume Algal Lab discovery campaigns with bounded experiments, evolving proposal strategies, primary-source comparison, independent checks, and publication of supported results. Use for the lab's outer research loop, not to treat a benchmark improvement as a new theorem.
---

# Algal discovery

Carry a research question from a recoverable experiment to an accurately scoped public result. Work from this repository's root. Read [the loop guide](../../../docs/discovery-loop.md) for command contracts, recovery, provider limits, and machine handoff. Read repository instructions and the campaign's latest evidence before selecting work; do not restart a completed literature search or repeat a consumed compute allocation.

## Recover the campaign

Find the current question, best supported result, incumbent strategy, failed approaches, pending checks, exact source revision, and remaining allowances. Preserve them in the task's private `runs/` directory. A new directory or computer does not renew the research budget. Keep publication-only allowances and scientific computation distinct. Reserve new work before dispatch, retain whole reservations, and leave uncertain remote operations unresolved until their effects are reconciled or explicitly abandoned. Follow the active host's required scheduler for the work being launched.

For a new finite campaign, record a falsifiable objective, the control strategy, the proposed strategy change and parent, allowed compute and dollar totals, development and regression cases, final evaluation rules, and stopping conditions. Choose one next experiment that would change the research decision. New API keys permit authentication; they do not grant spending authority.

## Iterate with evidence

For the supported network instrument, use `bun run discovery` to initialize, inspect context, propose or step, resume, seal, and confirm. Start with the no-key control. The runner reserves before evaluation, retains predictions and failures, keeps development and regression checks fixed, and checks connectivity through a second implementation. It accepts inert graph data only. Never reinterpret its score as a result about the mathematical papers.

Use an outer agent to propose bounded research and strategy changes. Record what the candidate predicts before evaluation, its exact parent, what failed, and the resulting update to the strategy. Keep the old strategy and its failed cases. Compare candidate strategies against the incumbent under matched tasks and allowances; freeze selection before a fresh final evaluation. A model's self-rating, one favorable example, or a reused holdout is insufficient to promote a research strategy.

Optional xAI/Gemini calls require an explicit finite configured budget and `--live`. Verify current official model/API/pricing information before a separately authorized live qualification. The shipped adapters have mock coverage, use synchronous requests, and offer bounded concurrency and multiple proposals per response; they do not promise provider batch discounts. Retain request IDs, reported model and usage, responses, and uncertain failures. Never put keys into prompts, logs, committed examples, or the publication package.

A different scientific instrument requires a reviewed evaluator or proof/certificate checking procedure with explicit input, source, time, and scope bindings. Keep model-authored code inert until reviewed. Preserve counterexamples and failed certificates; do not turn an obstruction for one proof family into a counterexample to the mathematical claim.

## Establish what the claim means and what is new

State every assumption, quantifier, constant, and equality case precisely. Distinguish an exact theorem, finite verified instance, numerical observation, heuristic search failure, and conjecture. Independently check a proposed result against its frozen proof, certificate, or dataset. A second model review is AI review, not human peer review.

Apply the Hraness Bio distinction between reading a source and reproducing its claim. Build a claim-to-source table: exact primary source and version; relevant theorem/proof location; its hypotheses and conclusion; substitution into the present setting; what follows directly; what is still different. Read the relevant proof, not just its abstract. Follow references and later citing work where accessible, inspect competing terminology, and use primary texts to test the most plausible rediscoveries. Identify missing coverage explicitly. Empty searches, inaccessible papers, snippets, and model recollection cannot establish historical priority. Credit known constructions and state unresolved novelty plainly.

Ask independent workers to examine the frozen mathematics, likely prior-art overlaps, and reader-facing claims when those are material. Give reviewers source identities and a bounded question. The integrator reads their actual evidence, resolves findings, and runs the applicable final gate; a worker's unexplained PASS is insufficient.

## Publish and continue

Admit only results supported within their stated scope. Update the relevant article in [`discoveries/articles/`](../../../discoveries/articles/) for stronger evidence or a correction; create a new article for a distinct result with a useful reader question. Update [`discoveries/manifest.json`](../../../discoveries/manifest.json) and its publication evidence. Export the committed, reviewed revision with `bun run discoveries:export --out PATH --revision EXACT_COMMIT --site-root JUNGLE` and use the normal repository validation workflow. Never turn a provider response directly into a blog mutation. Preserve previous release assets and dated change history.

Write an introduction a reader without mathematics, science, or programming training can understand. Explain the practical question, the supported result, and how it was reached before the technical detail. Use source-backed diagrams when they clarify the reasoning. End with a concise result and method recap, then link the papers, proofs, code, related discoveries, and open questions. Give citations exact source locations and explanatory labels suitable for the site's expandable references. Maintain separate mathematical and editorial reviews and disclose AI assistance accurately.

Run the repository's required checks, inspect rendered articles at desktop and mobile widths, verify citation disclosure and figure descriptions, and carry the task through its normal PR, merge, deployment, and live URL checks under the user's standing authorization. Record the article source revision, public URLs, release identities, and verification evidence. The CLI never publishes by itself; the outer agent owns this delivery step.

After publication or a rejected candidate, use the new evidence to select the next justified experiment while allowance remains. Stop dependent work at the campaign's declared limits or an unresolved authority, integrity, or qualification boundary. Leave a recoverable handoff with the strongest supported claim, explicit unresolved questions, remaining allowance, and the exact next test. Keep author emails unsent unless the user later explicitly changes that instruction.
