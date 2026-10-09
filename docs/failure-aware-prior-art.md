# Failure-aware execution: prior-art gate v1

**Date:** 2026-10-08
**Campaign:** `host-comparison-2026-10-08-v1`
**Decision status:** **established/reproduction; subsumed for the stated
correctness contract**. This is a bounded source comparison, not an exhaustive
literature search or a novelty verdict.

## Decision under test

The frozen local contract says: a synced dispatch intent followed by an
interruption becomes `uncertain`; it is never retried automatically; a complete
row needs a canonical receipt and one oracle-approved effect; queued work can be
cancelled; duplicate submission is rejected; and a different healthy job can
complete after observed host recovery. The effect may be durable while the host
result is unknown.

The question was whether that contract supplies a guarantee beyond write-ahead
logging (WAL), provider idempotency keys, transactional outboxes/delivery
semantics, fencing, and durable workflow engines. It does not. The local
artifact is useful as a reproducible cross-runtime **test contract and policy
choice**, not as a new recovery primitive, external-effect guarantee, or
production result.

## Claim-to-primary-source matrix

| ID | Primary source and exact location | Assumptions and directly supported guarantee | Substitution into this protocol and finding |
|---|---|---|---|
| WAL | C. Mohan et al., “ARIES: A Transaction Recovery Method,” *ACM TODS* 17(1), 1992, DOI [`10.1145/128765.128770`](https://doi.org/10.1145/128765.128770), §1.1 “Logging, Failures, and Recovery Methods,” pp. 95–98; the paragraph beginning “The WAL protocol asserts…” is also available in the [author-hosted copy](https://db.cs.berkeley.edu/cs262/Aries.pdf). | A stable log is forced before changed database pages; page LSNs support redo/undo after failure. The recoverable data is inside the logging/recovery system. | The synced journal is a WAL-like intent record, but `effects.jsonl` is deliberately separate. WAL orders local durable state; it cannot decide whether an independent external effect happened. **No extra guarantee.** |
| Provider idempotency | [Stripe API reference, “Idempotent requests”](https://docs.stripe.com/api/idempotent_requests), section “Idempotent requests,” accessed 2026-10-08. | The provider stores the first status/body for a key (including failures), compares later parameters, and retains keys only for a bounded period; validation/concurrent conflicts may not create a stored result. | A provider that honors this contract can safely retry the same operation within retention. The fixture has no provider key or remote reconciliation; its local duplicate refusal is a bounded admission rule, not a stronger provider guarantee. **No extra guarantee.** |
| Transactional outbox | Chris Richardson, [“Pattern: Transactional outbox”](https://microservices.io/patterns/data/transactional-outbox.html), headings “Forces,” “Solution,” and “Result context,” accessed 2026-10-08. | The business update and outbox message commit atomically in one database; a relay later publishes it. The relay may publish more than once, so consumers must be idempotent. | Durable dispatch intent plus a relay already covers the durable-intent/at-least-once shape. The local split effect log exposes the same atomicity gap rather than closing it. **No extra guarantee.** |
| Delivery semantics | [Apache Kafka 4.1 design, “Message Delivery Semantics”](https://kafka.apache.org/41/design/design/#message-delivery-semantics), accessed 2026-10-08, especially the paragraphs on producer network errors, idempotent producer sequence numbers, consumer offsets, and Kafka-to-Kafka transactions. | A producer that loses the response cannot know whether the message committed; resend is at-least-once unless broker deduplication/transactions apply. Exactly-once is scoped to cooperating Kafka topics and committed offsets, not arbitrary external effects. | The protocol’s `uncertain` state is the same ambiguity, made explicit instead of retried. The local oracle checks only the fixture log and cannot prove a remote effect. **No extra guarantee.** |
| Fencing/ownership | Burrows, [“The Chubby lock service for loosely-coupled distributed systems,” OSDI 2006](https://research.google.com/archive/chubby-osdi06.pdf), §2.4 “Locks and sequencers”; see also Kleppmann, [“Making the lock safe with fencing”](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html), accessed 2026-10-08. | Chubby issues a sequencer tied to lock generation; the recipient must validate it and reject stale requests. Lock-delay is only an imperfect fallback. Fencing requires a cooperative recipient. | The local owner pipe, observed-exit recovery, and single-writer lock are weaker than a distributed fence and explicitly are not a lease. No stale remote owner is fenced. **No extra guarantee.** |
| Durable workflow engine | [Temporal, “Workflow Execution overview,” paragraphs headed “Durability” and “Reliability,” and section “Replays”](https://docs.temporal.io/workflow-execution), plus [“Retry Policies,” sections “Overview,” “Default behavior,” and “Activity Execution”](https://docs.temporal.io/encyclopedia/retry-policies), accessed 2026-10-08. | A service persists event history and deterministic workflow replay across failure. Activities have automatic retry by default, configurable by a retry policy; external side effects still require an appropriate activity/provider contract. | A workflow engine can implement durable intent, recovery, and either retry or a no-retry policy. The frozen no-retry choice is a safety policy, not a new engine-level guarantee. **No extra guarantee.** |

## Independent source-location review receipt

On 2026-10-08, the designated task writer independently fetched and checked the
six matrix entries at their cited locations, including the assumptions and the
substitution into the frozen contract. The bounded observations were:

1. **ARIES §1.1, pp. 95–98:** the author-hosted PDF contains the WAL statement
   that log records describing changed data must be on stable storage before an
   updated page replaces the prior page, and describes page LSNs. This supports
   the WAL analogy only; it does not cover the separate effect log.
2. **Stripe “Idempotent requests”:** the page says the first status/body is
   saved for a key, later matching-key requests return that result, keys may be
   pruned after at least 24 hours, and parameters are compared. It also says
   validation/concurrent conflicts may have no saved result. The bounded local
   duplicate rule therefore is not provider idempotency.
3. **Transactional outbox, “Forces,” “Solution,” “Result context”:** the page
   requires the outbox write in the same database transaction and a separate
   relay; it explicitly warns that a relay can publish more than once and
   consumers must be idempotent. The split local effect log exposes, rather than
   solves, that gap.
4. **Kafka 4.1, “Message Delivery Semantics”:** the page states that a producer
   network error leaves commit status unknown, resend is at-least-once without
   deduplication, producer sequence numbers/transactions cover Kafka's own
   cooperating paths, and external destinations require cooperation. This is
   the same ambiguity represented by `uncertain`.
5. **Chubby §2.4, with the cited fencing note:** Chubby's sequencer carries lock
   name, mode, and generation; the recipient is expected to validate it, while
   lock-delay is explicitly imperfect. The local pipe and observed-exit rule
   provide no such recipient-enforced stale-owner rejection.
6. **Temporal “Durability,” “Reliability,” “Replays,” and retry-policy
   “Default behavior”/“Activity Execution”:** the service persists workflow
   state and resumes from recorded history; Activities retry by default, while
   Workflow Executions do not by default. Configurable retry/no-retry behavior
   is an engine policy, and does not make an external effect durable or fenced.

All six assumptions and substitutions match the matrix. The conservative
conclusion is retained: **no new guarantee beyond the named baselines**. This
review is a source comparison, not human peer review, an exhaustive search, a
novelty claim, or a production qualification. It does not change the frozen
uncertainty semantics.

## Second bounded review receipt (2026-10-09)

A separate bounded read checked the six cited locations directly against the
frozen protocol (`experiments/host-comparison/README.md`, `protocol.ts`, and
`protocol.test.ts`), `AGENTS.md`, and `docs/roadmap.md`. No search snippet or
model output was used as evidence; all six direct public reads succeeded.

- **ARIES §1.1:** the WAL paragraph requires the change log on stable storage
  before an updated page, with page LSNs for recovery. The protocol journal is
  analogous only for local intent; its separate effect log remains outside WAL.
- **Stripe idempotent requests:** the first status/body (including failures) is
  retained for a key, matching parameters are required, retention is bounded,
  and validation/concurrent conflicts need not save a result. Local duplicate
  refusal is therefore not provider idempotency.
- **Transactional outbox:** the business update and outbox write share one
  database transaction, then a relay publishes; relay duplicates require an
  idempotent consumer. The split effect log does not close that gap.
- **Kafka 4.1 delivery semantics:** a lost producer response leaves commit
  status unknown; producer sequence numbers/transactions cover Kafka's
  cooperating paths, while other destinations require cooperation. This matches
  explicit `uncertain`, not automatic retry.
- **Chubby §2.4 and fencing note:** a sequencer carries lock identity/mode/
  generation and the recipient must reject stale values; lock-delay is
  imperfect. The local owner pipe is not a distributed fence or lease.
- **Temporal durability/replay and retry policy:** event history/replay resumes
  workflows; Activities retry by default, Workflow Executions do not. Retry or
  no-retry remains policy and does not make an external effect durable or fenced.

**Review result:** no citation or claim-boundary repair was needed. The six
assumptions and substitutions still support only the conservative
**no-new-guarantee** conclusion. This is an AI/source check, not human peer
review, an exhaustive novelty search, or a production result. The frozen
`uncertain`/no-automatic-retry semantics remain unchanged. No timing,
delayed-transfer, provider, paid, or `runs/` operation was started; paid charge
was `$0`.

## Gap and stopping rule

The precise remaining boundary is operational, not novel: a real external effect
needs a provider contract (idempotency or reconciliation) and, where ownership
can overlap, recipient-enforced fencing. The local oracle cannot supply either.
The protocol therefore must not be described as exactly-once, distributed
recovery, provider durability, or a BEAM/Bun advantage. Delayed-transfer tests
are **not authorized by this gate**; they would only be justified by a separately
specified external contract and an independent review question.

## Review and accounting receipt

- Independent correctness review of the preceding local gate: six bounded
  checks passed; zero duplicate effects; no holdout or provider call. The
  source-location review above also passed all six checks.
- Source access failures preserved: the DuckDuckGo search returned a bot
  challenge; ACM’s hosted PDF returned HTTP 403; the first Berkeley PDF fetch
  timed out during extraction; and a Semantic Scholar Chubby lookup returned
  HTTP 429. Direct DOI, Berkeley, and Google-hosted primary sources were then
  read successfully. During this review, one local HTML extraction filter also
  rejected an overlong regular-expression interval; bounded direct extraction
  then succeeded. No paid request or charge resulted from these failures.
- Existing RSS/timing attempt remains unresolved because `/bin/ps` returned
  `EPERM`; no timing values were selected and it was not retried here.
- No timing, delayed-transfer test, provider request, or `runs/` artifact was
  started by this review. Paid calls: 0. Paid charge: `$0`. Remaining paid
  allowance: `$0`.
