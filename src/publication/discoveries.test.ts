import { describe, expect, test } from "bun:test";
import { cp, lstat, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { createHash } from "node:crypto";
import { assembleDiscoveries, exportCommittedDiscoveries, gitText } from "./discoveries";
import { writePublicationFile } from "../../scripts/export-discoveries";

const root = resolve(import.meta.dir, "../..");
const revision = "04878e1152f28005c72b83058c870d6c9070e81e";
const read = async (path: string) => readFile(resolve(root, path));
const manifest = async () => JSON.parse(await readFile(resolve(root, "discoveries/manifest.json"), "utf8"));

describe("public discovery export", () => {
  test("all canonical articles, citations, figures and review evidence resolve", async () => {
    const output = await assembleDiscoveries(await manifest(), revision, read);
    expect(output.bundle.articles.length).toBe(7);
    expect(output.figures.length).toBe(5);
    expect(output.bundle.articles.every((article) => !("bodyFile" in article))).toBe(true);
    expect(output.figures.every((figure) => /^[a-f0-9]{64}$/u.test(figure.sha256))).toBe(true);
  });
  test("missing review and unknown publication fields cannot enter the bundle", async () => {
    const missing = await manifest();
    delete missing.articles[0].admission;
    await expect(assembleDiscoveries(missing, revision, read)).rejects.toThrow("missing or unknown");
    const unknown = await manifest();
    unknown.articles[0].execute = "anything";
    await expect(assembleDiscoveries(unknown, revision, read)).rejects.toThrow("missing or unknown");
  });
  test("review must cover the update and have its own qualifying admission", async () => {
    const stale = await manifest();
    const reviewTime = Date.parse(stale.articles[0].provenance.reviewedAt);
    stale.articles[0].updated = new Date(reviewTime + 86_400_000).toISOString().slice(0, 10);
    await expect(assembleDiscoveries(stale, revision, read)).rejects.toThrow("current update");
    const low = await manifest();
    low.articles[0].admission.scores.originalEvidence = 0;
    await expect(assembleDiscoveries(low, revision, read)).rejects.toThrow("threshold");
  });
  test("source paths and revisions cannot become arbitrary Git or filesystem reads", async () => {
    const traversal = await manifest();
    traversal.articles[0].bodyFile = "../../.env";
    await expect(assembleDiscoveries(traversal, revision, read)).rejects.toThrow("Body path");
    await expect(assembleDiscoveries(await manifest(), "HEAD:.env", read)).rejects.toThrow("exact Git commit");
  });
  test("unresolved references and duplicate routes are rejected", async () => {
    const reference = await manifest();
    reference.articles[0].citations[0].id = "not-in-body";
    await expect(assembleDiscoveries(reference, revision, read)).rejects.toThrow("Citations");
    const duplicate = await manifest();
    duplicate.articles.push(duplicate.articles[0]);
    await expect(assembleDiscoveries(duplicate, revision, read)).rejects.toThrow("duplicates");
  });
  test("unsafe schemes and private credential-bearing URLs are rejected", async () => {
    for (const url of ["javascript:alert(1)", "https://secret@example.com/paper"]) {
      const unsafe = await manifest();
      unsafe.articles[0].artifacts[0].url = url;
      await expect(assembleDiscoveries(unsafe, revision, read)).rejects.toThrow("credential-free HTTPS");
    }
  });
  test("titled, reference, autolink and encoded destinations cannot bypass link policy", async () => {
    for (const fragment of [
      '[x](javascript:alert%281%29 "title")',
      '[x][source]\n\n[source]: javascript:alert%281%29 "title"',
      '[source][]\n\n[source]: javascript:alert%281%29',
      '[source]\n\n[source]: javascript:alert%281%29',
      '<javascript:alert%281%29>',
      '[x](java&#x73;cript&#58;alert%281%29)',
      '[x](java&NewLine;script:alert%281%29)',
      '[x](javascript\\:alert%281%29)',
      '[x](https://user&#64;example.com/paper "title")',
      '[x](https://user\\@example.com/paper)',
      '[![figure](/discoveries/figures/reflection-constants.svg)](javascript:alert%281%29 "title")',
    ]) {
      const data = await manifest();
      const path = "discoveries/" + data.articles[0].bodyFile;
      const altered = async (name: string) => name === path ? Buffer.from((await read(name)).toString("utf8") + "\n\n" + fragment + "\n") : read(name);
      await expect(assembleDiscoveries(data, revision, altered)).rejects.toThrow("article link");
    }
  });
  test("parsed references enforce registered local figures and known article routes", async () => {
    for (const [fragment, error] of [
      ['![x](https://example.com/x.svg "title")', "registered local SVG"],
      ['![x][figure]\n\n[figure]: https://example.com/x.svg "title"', "registered local SVG"],
      ['![x](https&#58;//example.com/x.svg)', "registered local SVG"],
      ['![x](/discoveries/figures/missing\\.svg "title")', "Unregistered figure"],
      ['[x][article]\n\n[article]: /discoveries/missing-article "title"', "Missing article link"],
    ]) {
      const data = await manifest();
      const path = "discoveries/" + data.articles[0].bodyFile;
      const altered = async (name: string) => name === path ? Buffer.from((await read(name)).toString("utf8") + "\n\n" + fragment + "\n") : read(name);
      await expect(assembleDiscoveries(data, revision, altered)).rejects.toThrow(error);
    }
  });
  test("safe parsed destinations preserve original Markdown and figure bytes", async () => {
    for (const image of [
      '![figure](/discoveries/figures/reference-only.svg "Titled figure")',
      '![figure][diagram]\n\n[diagram]: /discoveries/figures/reference-only.svg "Reference figure"',
      '![figure](/discoveries/figures/reference\\-only.svg)',
      '![figure](/discoveries/figures/reference&#45;only.svg)',
    ]) {
      const data = await manifest();
      const bytes = await read("discoveries/figures/" + data.figures[0]);
      data.figures.push("reference-only.svg");
      const path = "discoveries/" + data.articles[0].bodyFile;
      const original = (await read(path)).toString("utf8");
      const body = original + '\n\n' + image + '\n\n[x](https&#58;//example.com/a\\(b\\)?x=1&amp;y=2 "Title")\n\n<https://example.com/>\n\n[local][article]\n\n[article]: /discoveries/' + data.articles[1].slug + '\n\n`[example](javascript:alert(1))`\n';
      const altered = async (name: string) => name === path ? Buffer.from(body) : name.endsWith("/reference-only.svg") ? bytes : read(name);
      const output = await assembleDiscoveries(data, revision, altered);
      expect(output.bundle.articles[0]!.bodyMarkdown).toBe(body);
      const figure = output.figures.find((entry) => entry.name === "reference-only.svg")!;
      expect(Buffer.from(figure.bytes).equals(bytes)).toBe(true);
      expect(figure.sha256).toBe(createHash("sha256").update(bytes).digest("hex"));
    }
  });
  test("active SVG content and raw HTML are not exported", async () => {
    const unsafeSvg = async (path: string) => path.endsWith(".svg")
      ? new TextEncoder().encode('<svg xmlns="http://www.w3.org/2000/svg"><title id="t">Unsafe</title><script>alert(1)</script></svg>')
      : read(path);
    await expect(assembleDiscoveries(await manifest(), revision, unsafeSvg)).rejects.toThrow("Unsafe");
    const unsafeBody = async (path: string) => path.endsWith(".md")
      ? new TextEncoder().encode("<iframe src='https://example.com'></iframe>")
      : read(path);
    await expect(assembleDiscoveries(await manifest(), revision, unsafeBody)).rejects.toThrow("Raw HTML");
  });
  test("namespaced scripting, animation and CSS cannot enter static diagrams", async () => {
    for (const content of [
      '<svg xmlns="http://www.w3.org/2000/svg" xmlns:s="http://www.w3.org/2000/svg"><title id="t">Unsafe</title><s:script>alert(1)</s:script></svg>',
      '<svg xmlns="http://www.w3.org/2000/svg"><title id="t">Unsafe</title><a><animate attributeName="href" values="javascript:alert(1)"/><text>Click</text></a></svg>',
      '<svg xmlns="http://www.w3.org/2000/svg"><title id="t">Unsafe</title><style>@import "https://example.com";</style></svg>',
    ]) {
      const unsafeRead = async (path: string) => path.endsWith(".svg") ? new TextEncoder().encode(content) : read(path);
      await expect(assembleDiscoveries(await manifest(), revision, unsafeRead)).rejects.toThrow("Unsafe");
    }
  });
  test("an exact commit exports original bytes despite dirty source and rejects invalid UTF-8", async () => {
    const fixture = await mkdtemp(join(tmpdir(), "algal-discoveries-git-"));
    try {
      await cp(join(root, "discoveries"), join(fixture, "discoveries"), { recursive: true });
      const data = await manifest();
      const figureName = data.figures[0] as string;
      const figurePath = join(fixture, "discoveries/figures", figureName);
      const bytes = Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), await readFile(figurePath)]);
      await writeFile(figurePath, bytes);
      await gitText(fixture, ["init", "--quiet"]);
      const commit = async () => {
        await gitText(fixture, ["add", "--", "discoveries"]);
        await gitText(fixture, ["-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "-c", "user.name=Algal fixture", "-c", "user.email=fixture@example.invalid", "commit", "--quiet", "-m", "Publication fixture"]);
        return (await gitText(fixture, ["rev-parse", "HEAD"])).trim();
      };
      const selected = await commit();
      const bodyPath = join(fixture, "discoveries", data.articles[0].bodyFile as string);
      const originalBody = await readFile(bodyPath);
      await writeFile(bodyPath, "<script>dirty source must stay out</script>");
      const output = await exportCommittedDiscoveries(fixture, selected);
      const figure = output.figures.find((item) => item.name === figureName)!;
      expect(Buffer.from(figure.bytes).equals(bytes)).toBe(true);
      expect(figure.sha256).toBe(createHash("sha256").update(bytes).digest("hex"));
      expect(output.bundle.articles[0]!.bodyMarkdown).toBe(originalBody.toString("utf8"));
      expect(output.bundle.source.revision).toBe(selected);
      await writeFile(bodyPath, originalBody);
      const titleEnd = bytes.indexOf(Buffer.from("</title>"));
      expect(titleEnd).toBeGreaterThan(0);
      const invalid = Buffer.concat([bytes.subarray(0, titleEnd), Buffer.from([0xff]), bytes.subarray(titleEnd)]);
      await writeFile(figurePath, invalid);
      await expect(exportCommittedDiscoveries(fixture, await commit())).rejects.toThrow();
      await writeFile(figurePath, bytes);
      const manifestPath = join(fixture, "discoveries/manifest.json");
      const manifestBytes = await readFile(manifestPath);
      const titleStart = manifestBytes.indexOf(Buffer.from(JSON.stringify(data.articles[0].title))) + 1;
      expect(titleStart).toBeGreaterThan(0);
      await writeFile(manifestPath, Buffer.concat([manifestBytes.subarray(0, titleStart), Buffer.from([0xff]), manifestBytes.subarray(titleStart)]));
      await expect(exportCommittedDiscoveries(fixture, await commit())).rejects.toThrow();
    } finally { await rm(fixture, { recursive: true, force: true }); }
    // Three real commits and bounded Git reads need more than Bun's 5s default on shared CI.
  }, 30_000);
  test("publication replaces a leaf symlink without overwriting its target", async () => {
    const fixture = await mkdtemp(join(tmpdir(), "algal-discoveries-write-"));
    try {
      const target = join(fixture, "preserved.txt");
      const destination = join(fixture, "content.generated.json");
      await writeFile(target, "preserved");
      await symlink(target, destination);
      await writePublicationFile(destination, "published");
      expect(await readFile(target, "utf8")).toBe("preserved");
      expect(await readFile(destination, "utf8")).toBe("published");
      expect((await lstat(destination)).isSymbolicLink()).toBe(false);
    } finally { await rm(fixture, { recursive: true, force: true }); }
  });
});
