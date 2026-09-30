import { mkdir, readFile, realpath, writeFile, rename, rm } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { exportCommittedDiscoveries, gitText, previewDiscoveries } from "../src/publication/discoveries";

/** Rename replaces a destination symlink itself, without writing through it. */
export async function writePublicationFile(path: string, bytes: string | Uint8Array): Promise<void> {
  const temporary = join(dirname(path), ".discovery-export-" + randomUUID() + ".tmp");
  try {
    await writeFile(temporary, bytes, { flag: "wx", mode: 0o644 });
    await rename(temporary, path);
  } finally { await rm(temporary, { force: true }); }
}

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  const values = new Map<string, string>();
  let preview = false;
  for (let index = 0; index < argv.length; index++) {
    const key = argv[index]!;
    if (key === "--preview" && !preview) { preview = true; continue; }
    if (!["--revision", "--out", "--site-root"].includes(key) || values.has(key) || !argv[index + 1] || argv[index + 1]!.startsWith("--")) throw new Error("Usage: bun run discoveries:export --out PATH [--revision SHA] [--site-root JUNGLE] [--preview]");
    values.set(key, argv[++index]!);
  }
  if (!values.has("--out")) throw new Error("--out is required");
  if (preview && values.has("--site-root")) throw new Error("Preview exports cannot update a publication site");
  const root = resolve(import.meta.dir, "..");
  const revision = values.get("--revision") ?? (await gitText(root, ["rev-parse", "HEAD"])).trim();
  const result = preview ? await previewDiscoveries(root, revision) : await exportCommittedDiscoveries(root, revision);
  const bytes = JSON.stringify(result.bundle, null, 2) + "\n";
  const out = resolve(values.get("--out")!);
  await mkdir(join(out, "figures"), { recursive: true });
  await writePublicationFile(join(out, "content.generated.json"), bytes);
  for (const figure of result.figures) await writePublicationFile(join(out, "figures", figure.name), figure.bytes);
  await writePublicationFile(join(out, "export.json"), JSON.stringify({
    schemaVersion: 1, previewOnly: preview, sourceRevision: revision,
    contentSha256: createHash("sha256").update(bytes).digest("hex"),
    articles: result.bundle.articles.map((article) => article.slug),
    figures: result.figures.map(({ name, sha256 }) => ({ name, sha256 })),
  }, null, 2) + "\n");
  if (values.has("--site-root")) {
    const site = await realpath(resolve(values.get("--site-root")!));
    const origin = (await gitText(site, ["remote", "get-url", "origin"])).trim();
    if (!/^(?:https:\/\/github\.com\/|git@github\.com:)hraness\/jungle(?:\.git)?$/u.test(origin)) throw new Error("Site origin must be hraness/jungle");
    const project = join(site, "projects/hraness");
    const sitePackage = JSON.parse(await readFile(join(project, "package.json"), "utf8")) as { name?: string };
    if (sitePackage.name !== "@jungle/hraness") throw new Error("Unexpected website package");
    const contentDirectory = join(project, "app/discoveries");
    if (await realpath(contentDirectory) !== contentDirectory) throw new Error("Publication content directory must not be a symlink");
    const figureDirectory = join(project, "public/discoveries/figures");
    await mkdir(figureDirectory, { recursive: true });
    if (await realpath(figureDirectory) !== figureDirectory) throw new Error("Publication figure directory must not be a symlink");
    await writePublicationFile(join(contentDirectory, "content.generated.json"), bytes);
    for (const figure of result.figures) await writePublicationFile(join(figureDirectory, figure.name), figure.bytes);
  }
  console.log(JSON.stringify({ ok: true, previewOnly: preview, sourceRevision: revision, articles: result.bundle.articles.length, figures: result.figures.length, out }));
}

if (import.meta.main) main().catch((error: unknown) => { console.error(error instanceof Error ? error.message : "Publication export failed"); process.exitCode = 1; });
