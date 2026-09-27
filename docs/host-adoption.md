# Applying the host and optimizer experiments

Keep ALGAL's portable program and execution-record formats. The host comparison
runs the same program behind Bun and Elixir supervisors, and measures ownership,
queueing, cancellation, and failure behavior. Neither experiment requires a VM
change or qualifies a production Elixir service.

## Persistent services

Use the product's existing durable identity and effect journal. Record dispatch
intent before launching a worker. Keep waiting work finite, check its deadline at
admission, and associate it with the initiating session or process. Owner death
can cancel queued work; dispatched work needs settlement or explicit reconciliation.
Process restart alone never authorizes retrying a remote write.

The Cloud implementation uses its existing journal for each evolution epoch. A
recovered owner fences earlier continuations. Reconciliation requires the exact
observed dispatch identity, owner epoch, and version; a later epoch cannot satisfy
an earlier observation. Uncertain calls remain uncertain. The default production
broker path stays disabled until an observer can reconcile the required output.

Textbutler is the consumer pilot: its existing contact programs use the task API
with the same prompt and effective limits, and its read-only contact view includes
operation state. Message-send authority remains in its existing host workflow.
The synthetic response study evaluates that policy shape; it does not qualify live
messaging or show a production improvement.

xcb's managed daemons already persist intent, suspend, and resume from settled
child results. Spongev2's project services also retain host-specific identity and
settlement rules. Apply the same queue/deadline/owner observations to those hosts
where useful; the experiment does not justify replacing their schedulers or
creating a second retry authority. A later integration should demonstrate one
real operational problem before adding another always-on service.

## Portable and pure execution

Clankdar needs the official portable evaluator in Bun and workerd. Slopcamera
rejects model/tool effects during scene execution. Alt uses browser execution,
IndexedDB, and local model inference. Keep these profiles independent of server
supervision. The core changes compile tasks into existing manifests and leave the
Rust evaluator and canonical receipt format unchanged. Cloud's workerd checks and
core's browser/native checks qualify the relevant package paths; these are not
claims that every consumer has upgraded its dependency.

Ghostget Skills can retain fixed, bounded CLI workflows and offline replay. The
new task API is optional for model decisions; it does not replace tool authority
or require a background service.

## Optimization experiments

Start with a fixed task, then labeled examples. Use source-disjoint training,
selection, and audit sets and retain every attempted candidate and cost. The live
comparison found no advantage from feedback over labeled examples. Its retained
knowledge follow-up kept the original task after a validation tie.

Bio, Pattern Language, and Sloptrade's evolution lab can use the same split and
accounting discipline. Their scientific or trading claims still require their
own evaluators and untouched audit data. A successful replay or larger candidate
portfolio is not evidence of better decisions.

The implemented pilot repositories are ALGAL, ALGAL Cloud, Algal Lab, and
Textbutler. The other projects above are compatibility constraints and follow-on
integration guidance; this change does not edit or deploy them.
