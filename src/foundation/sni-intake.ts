import { sha256 } from "./datasets";

/** Source identities are Git objects, not local task-file reads. No test JSON is fetched. */
export const SNI = {
  commit: "55a365637381ce7f3748fa2eac7aef1a113bbb82",
  tree: "cc84a807512603c2a8e5978cd067f5397dff8edd",
  splits: {
    train: { count: 756, sha256: "7ba69b22c1d6096f9747290782e5e0f358728407b065c4bd561fdf4f6239db1c" },
    test: { count: 119, sha256: "8b2068c1e0c5e545abd1172fcf83b17935a791dae19912b5cf68e29355af3cba" },
    excluded: { count: 738, sha256: "5d1e0c00933ae63ee73a527e9d0e5440527898ed8dbbe49f66e803495319faa8" },
  },
} as const;
export type SniSplit = keyof typeof SNI.splits;
export type TaskRef = Readonly<{ task: string; split: SniSplit; blobOid: string }>;
const order: readonly SniSplit[] = ["train", "test", "excluded"];
const idPattern = /^task[0-9]{3,4}_[a-zA-Z0-9_.-]+$/;
const oidPattern = /^[0-9a-f]{40}$/;

/** The TSV enumerates every task digest in upstream split order. Its SHA-256 is the public index pin. */
export function pinTaskIndex(tree: unknown, splitFiles: Record<SniSplit, Uint8Array>) {
  if (!tree || typeof tree !== "object" || Array.isArray(tree)) throw Error("invalid Git tree");
  const root = tree as Record<string, unknown>;
  if (root.sha !== SNI.tree || root.truncated !== false || !Array.isArray(root.tree)) throw Error("Git tree identity or completeness mismatch");
  const blobs = new Map<string, string>();
  for (const raw of root.tree) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) throw Error("invalid Git tree entry");
    const item = raw as Record<string, unknown>;
    if (typeof item.path !== "string" || !item.path.startsWith("tasks/") || !item.path.endsWith(".json")) continue;
    const task = item.path.slice("tasks/".length, -".json".length);
    if (!idPattern.test(task) || item.type !== "blob" || typeof item.sha !== "string" || !oidPattern.test(item.sha) || blobs.has(task)) throw Error("invalid or duplicate task blob");
    blobs.set(task, item.sha);
  }
  const seen = new Set<string>(), refs: TaskRef[] = [];
  for (const split of order) {
    const bytes = splitFiles[split], pin = SNI.splits[split];
    if (!(bytes instanceof Uint8Array) || sha256(bytes) !== pin.sha256) throw Error(`split digest mismatch: ${split}`);
    const names = new TextDecoder("utf-8", { fatal: true }).decode(bytes).trimEnd().split("\n");
    if (names.length !== pin.count) throw Error(`split count mismatch: ${split}`);
    for (const task of names) {
      if (!idPattern.test(task) || seen.has(task)) throw Error("invalid or cross-split duplicate task id");
      const blobOid = blobs.get(task);
      if (!blobOid) throw Error(`task absent from pinned tree: ${task}`);
      seen.add(task); refs.push({ task, split, blobOid });
    }
  }
  if (seen.size !== blobs.size) throw Error("tree contains unassigned task files");
  const tsv = refs.map(({ split, task, blobOid }) => `${split}\t${task}\t${blobOid}\n`).join("");
  return { refs, tsv, sha256: sha256(tsv) };
}

/** Only separately supplied, metadata-only sidecars may enter this function.
 * A sidecar is NOT an authenticated upstream extract: independent provenance review is still needed.
 * The closed shape makes accidental ingestion of Instances, examples or outputs fail. */
export type TaskMetadata = Readonly<{ task: string; Source: readonly string[]; Categories: readonly string[]; "Instance License": readonly string[] }>;
function strings(value: unknown, key: string, allowEmpty = false): string[] {
  if (!Array.isArray(value) || value.length > 12 || (!allowEmpty && !value.length)) throw Error(`invalid ${key}`);
  return value.map((item: unknown) => {
    if (typeof item !== "string" || !item.trim() || Buffer.byteLength(item) > 256) throw Error(`invalid ${key}`);
    return item.trim();
  });
}
export function parseTaskMetadata(value: unknown): TaskMetadata {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("metadata-only object required");
  const row = value as Record<string, unknown>;
  const keys = ["task", "Source", "Categories", "Instance License"];
  if (Object.keys(row).length !== keys.length || keys.some(key => !Object.hasOwn(row, key))) throw Error("metadata-only fields required; instances and outputs forbidden");
  if (typeof row.task !== "string" || !idPattern.test(row.task)) throw Error("invalid task id");
  return { task: row.task, Source: strings(row.Source, "Source"), Categories: strings(row.Categories, "Categories", true), "Instance License": strings(row["Instance License"], "Instance License") };
}

// Reviewed conservative aliases, not a claim that all derived datasets are covered.
// In particular an official exclusion does not make a train/test derivative safe.
export function sourceKey(raw: string): string {
  const key = raw.normalize("NFKC").toLowerCase().trim().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
  if (!key) throw Error("empty source key");
  if (["wsc", "wscfixed", "enhanced_wsc", "mwsc", "winograd_schema_challenge", "superglue_wsc"].includes(key)) return "family:wsc";
  if (["squad", "squad_1_1", "squad_2_0", "squad_v1_1", "squad_v2_0"].includes(key)) return "family:squad";
  if (["qasc", "eqasc", "eqasc_perturbed"].includes(key)) return "family:qasc";
  return `source:${key}`;
}
const permitted = new Set(["apache-2.0", "mit", "cc0-1.0", "cc by 4.0", "cc by-sa 4.0", "cc by 3.0", "cc by-sa 3.0"]);
function licenseOK(values: readonly string[]): boolean {
  return values.every(value => permitted.has(value.trim().toLowerCase()));
}

/** Quarantine connected groups, not individual duplicates; excluded tasks can bridge sources.
 * This is a diagnostic on supplied sidecars, NEVER an admission or holdout release. */
export function auditMetadata(refs: readonly TaskRef[], sidecars: readonly unknown[]) {
  if (refs.length < 1 || refs.length > 2000 || sidecars.length !== refs.length) throw Error("incomplete metadata sidecars");
  const byId = new Map<string, TaskRef>();
  for (const ref of refs) {
    if (!idPattern.test(ref.task) || !oidPattern.test(ref.blobOid) || !order.includes(ref.split) || byId.has(ref.task)) throw Error("invalid task index");
    byId.set(ref.task, ref);
  }
  const metadata = new Map<string, TaskMetadata>();
  for (const raw of sidecars) {
    const row = parseTaskMetadata(raw);
    if (!byId.has(row.task) || metadata.has(row.task)) throw Error("missing, duplicate or unindexed metadata");
    metadata.set(row.task, row);
  }
  const parent = new Map<string, string>();
  function find(key: string): string {
    if (!parent.has(key)) parent.set(key, key);
    const p = parent.get(key)!;
    if (p !== key) parent.set(key, find(p));
    return parent.get(key)!;
  }
  function unite(a: string, b: string) { parent.set(find(a), find(b)); }
  const sources = new Map<string, string[]>();
  for (const [task, row] of metadata) {
    const keys = [...new Set(row.Source.flatMap(raw => raw.split(";").map(sourceKey)))];
    if (!keys.length) throw Error("empty Source");
    for (const key of keys.slice(1)) unite(keys[0]!, key);
    sources.set(task, keys);
  }
  const groups = new Map<string, TaskRef[]>();
  for (const ref of refs) {
    const root = find(sources.get(ref.task)![0]!);
    groups.set(root, [...(groups.get(root) ?? []), ref]);
  }
  const collisionTasks = new Set<string>(), collisions: string[][] = [];
  for (const members of groups.values()) {
    if (members.some(row => row.split === "train") && members.some(row => row.split === "test")) {
      const tasks = members.map(row => row.task).sort();
      tasks.forEach(task => collisionTasks.add(task)); collisions.push(tasks);
    }
  }
  collisions.sort((a, b) => a[0]!.localeCompare(b[0]!));
  const unknownLicense = refs.filter(ref => !licenseOK(metadata.get(ref.task)!["Instance License"])).map(ref => ref.task).sort();
  const eligible = { train: 0, test: 0 };
  for (const ref of refs) {
    if (ref.split !== "excluded" && !collisionTasks.has(ref.task) && !unknownLicense.includes(ref.task)) eligible[ref.split]++;
  }
  return { collisions, unknownLicense, eligible, disposition: "review-required" as const };
}
