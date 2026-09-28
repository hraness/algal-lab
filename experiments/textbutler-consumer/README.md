# Textbutler captured-case study

This importer replays actual retained Textbutler model runs without calling a
provider. It separates observed output from independent annotations. Reproducing
a model's recorded choice does not show that the choice was good.

Export explicitly from Textbutler with its `scripts/export-textbutler-study.ts`
command. Keep the resulting file in an owned private directory, outside Git.
The exporter reads the existing journal without changing settings, messages or
SQLite records. It keeps bounded source digests, the current host task and the
original manifests and receipts. It never reads provider credentials.

```sh
bun experiments/textbutler-consumer/cli.ts inspect /private/study/captured.json
bun experiments/textbutler-consumer/cli.ts annotate /private/study/captured.json /private/study/annotations.json
```

The annotation template starts with every label `unknown`. A named owner or
independent reviewer supplies `respond` or `silent` and a rationale under the
versioned rubric in `corpus.ts`; unknown cases remain excluded. Do not copy the
observed output into labels. The rubric concerns the decision to answer, not
reply correctness, tone, helpfulness or satisfaction.

Freeze complete conversation groups before evaluation using a private JSON
array of `{sourceId, split}` records, one per exported group. All three splits
need independently labeled cases. Fewer than three groups is insufficient;
splitting overlapping messages from one conversation does not solve that.

```sh
bun experiments/textbutler-consumer/cli.ts freeze /private/study/captured.json /private/study/annotations.json /private/study/partitions.json /private/study/frozen.json
```

Every output requires a new filename and mode-0700 parent. Files are mode 0600.
The CLI prints only counts and digests. Public test fixtures are synthetic.
Actual captures, labels, examples and complete study archives remain private.
An evaluated artifact does not authorize messages, change a contact's tools,
or establish that its labels are true.

`compareTextbutlerTasks` in `study.ts` evaluates the same frozen cases with fixed
instructions and then training-only labeled examples. Each campaign has explicit
work, run and attempt ceilings; the comparison freezes the decision scorer and
replays both complete archives offline. It returns the portable selected task
and its archive for a host's separate admission decision. No provider is chosen
implicitly. A caller must supply an admitted executor and explicitly authorize
any private-data inference. Complete outputs can contain personal examples and
must be written privately; do not print the comparison's changed instructions or
examples in public summaries. Cross-contact examples must not be installed into
a contact's live response program.

Synthetic tests demonstrate this comparison and artifact transport. They do not
measure real-world usefulness. A capture containing two conversation groups and
no independent labels can be replayed and inspected, but cannot establish a
train/validation/holdout effectiveness result.

Artifacts containing labeled conversation examples are private research outputs. Textbutler refuses them for contact shadow installation or execution because the current transport cannot prove that every example belongs to the target contact.
