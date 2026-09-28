import { annotationTemplate, freezeCorpus, importCapturedCorpus } from "./corpus";
import { readPrivateJson, writePrivateJson } from "./private-files";

const [command, input, ...rest] = process.argv.slice(2);
try {
  if (!input || !["inspect", "annotate", "freeze"].includes(command ?? "")) throw Error("Usage");
  const corpus = await importCapturedCorpus(await readPrivateJson(input));
  if (command === "inspect" && !rest.length) console.log(JSON.stringify({ digest: corpus.digest, cases: corpus.cases.length, groups: corpus.groups.length,
    omitted: corpus.omitted, replayed: corpus.cases.length, labels: "absent", threeWayGroupSplitAvailable: corpus.groups.length >= 3, providerCalls: 0 }));
  else if (command === "annotate" && rest.length === 1) { await writePrivateJson(rest[0]!, annotationTemplate(corpus)); console.log(JSON.stringify({ cases: corpus.cases.length, labels: "unknown", providerCalls: 0 })); }
  else if (command === "freeze" && rest.length === 3) {
    const frozen = freezeCorpus(corpus, await readPrivateJson(rest[0]!), await readPrivateJson(rest[1]!));
    await writePrivateJson(rest[2]!, frozen); console.log(JSON.stringify({ digest: frozen.digest, cases: frozen.cases.length, excludedUnknown: frozen.excludedUnknown, providerCalls: 0 }));
  } else throw Error("Usage");
} catch { console.error("Private corpus operation failed. Check command arguments, source integrity, private paths and explicit independent labels/group partitions. No message content is printed."); process.exitCode = 1; }
