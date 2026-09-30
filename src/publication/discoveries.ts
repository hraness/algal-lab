import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

type ObjectValue = Record<string, unknown>;
export type PublishedDiscovery = ObjectValue & { slug: string; bodyMarkdown: string };
export type DiscoveryExport = {
  bundle: { schemaVersion: 1; source: { repository: string; revision: string }; articles: PublishedDiscovery[] };
  figures: { name: string; bytes: Uint8Array; sha256: string }[];
};
const REPOSITORY = "https://github.com/hraness/algal-lab";
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/u;
const SCORES = ["readerUtility", "originalEvidence", "factualConfidence", "hostFit", "voiceIntegrity", "maintenanceValue"] as const;
const ARTICLE_KEYS = ["slug", "title", "description", "date", "updated", "topic", "claimScope", "bodyFile", "citations", "artifacts", "relatedSlugs", "provenance", "admission"];
const SVG_ELEMENTS = new Set(["svg", "title", "desc", "g", "path", "line", "polyline", "polygon", "rect", "circle", "ellipse", "text", "tspan"]);
const SVG_ATTRIBUTES = new Set(["xmlns", "viewBox", "width", "height", "role", "aria-labelledby", "id", "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "d", "points", "fill", "stroke", "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin", "opacity", "fill-opacity", "stroke-opacity", "font-family", "font-size", "font-weight", "text-anchor", "transform"]);

/** A static diagram vocabulary; links, CSS, namespaces and animation cannot enter. */
function staticSvg(source: string): void {
  const stack: string[] = [];
  let offset = 0;
  let roots = 0;
  for (const match of source.matchAll(/<[^>]*>/gu)) {
    const preceding = source.slice(offset, match.index);
    if (preceding.includes("<") || (!stack.length && preceding.trim())) throw new Error("Unsafe SVG text");
    offset = match.index + match[0].length;
    const close = /^<\/([A-Za-z][A-Za-z0-9-]*)\s*>$/u.exec(match[0]);
    if (close) {
      if (stack.pop() !== close[1]) throw new Error("Unsafe SVG structure");
      continue;
    }
    const open = /^<([A-Za-z][A-Za-z0-9-]*)([\s\S]*?)(\/?)>$/u.exec(match[0]);
    if (!open || !SVG_ELEMENTS.has(open[1]!)) throw new Error("Unsafe SVG element");
    if (!stack.length && (open[1] !== "svg" || ++roots !== 1)) throw new Error("Unsafe SVG root");
    let attributes = open[2]!;
    const seen = new Set<string>();
    while (attributes.trim()) {
      const attribute = /^\s+([A-Za-z][A-Za-z0-9-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/u.exec(attributes);
      if (!attribute || !SVG_ATTRIBUTES.has(attribute[1]!) || seen.has(attribute[1]!)) throw new Error("Unsafe SVG attribute");
      const name = attribute[1]!;
      const value = attribute[2] ?? attribute[3]!;
      if (/[<&]/u.test(value) || (name === "xmlns" ? value !== "http://www.w3.org/2000/svg" : /(?:url\s*\(|javascript:|data:|https?:)/iu.test(value))) throw new Error("Unsafe SVG attribute value");
      seen.add(name);
      attributes = attributes.slice(attribute[0].length);
    }
    if (!open[3]) stack.push(open[1]!);
  }
  if (roots !== 1 || stack.length || source.slice(offset).trim()) throw new Error("Unsafe SVG structure");
}

function object(value: unknown, keys: readonly string[], label: string): ObjectValue {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error(label + " must be an object");
  const data = value as ObjectValue;
  if (Object.keys(data).length !== keys.length || keys.some((key) => !(key in data))
    || Object.keys(data).some((key) => !keys.includes(key))) throw new Error(label + " has missing or unknown fields");
  return data;
}
function string(value: unknown, label: string, max = 2000): string {
  if (typeof value !== "string" || value.trim().length === 0 || value.length > max
    || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/u.test(value)) throw new Error(label + " must be bounded nonempty text");
  return value;
}
function list(value: unknown, label: string, max: number, min = 0): unknown[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) throw new Error(label + " has invalid length");
  return value;
}
function slug(value: unknown, label: string): string {
  const result = string(value, label, 120);
  if (!SLUG.test(result)) throw new Error(label + " must be a lowercase slug");
  return result;
}
function date(value: unknown, label: string): string {
  const result = string(value, label, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(result)
    || !Number.isFinite(Date.parse(result))
    || new Date(result).toISOString().slice(0, 10) !== result) throw new Error(label + " is not an ISO date");
  return result;
}
function https(value: unknown, label: string): string {
  const result = string(value, label, 3000);
  const url = new URL(result);
  if (url.protocol !== "https:" || url.username || url.password) throw new Error(label + " must be credential-free HTTPS");
  return result;
}
function unique(values: string[], label: string): void {
  if (new Set(values).size !== values.length) throw new Error(label + " contains duplicates");
}

type MarkdownDestination = { kind: "link" | "image"; target: string };

/** Bun's callbacks expose destination syntax before CommonMark unescaping.
 * Decode escapes and entities in one pass, so an escaped ampersand cannot
 * introduce a second entity. Let the installed parser decode entity names. */
function markdownDestination(value: string): string {
  return value.replace(/\\([\u0021-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007e])|&(?:#[xX][\da-fA-F]+|#\d+|[A-Za-z][A-Za-z\d]*);/gu,
    (token: string, escaped: string | undefined) => escaped ?? Bun.markdown.render(token));
}

/** Parse the same link forms a Markdown renderer can activate; never rewrite
 * the authored body. Code examples remain text, and raw HTML is rejected. */
function markdownDestinations(body: string): MarkdownDestination[] {
  const destinations: MarkdownDestination[] = [];
  Bun.markdown.render(body, {
    link: (_children, { href }) => { destinations.push({ kind: "link", target: markdownDestination(href) }); return ""; },
    image: (_children, { src }) => { destinations.push({ kind: "image", target: markdownDestination(src) }); return ""; },
    html: () => { throw new Error("Raw HTML is not supported in discovery articles"); },
  }, { autolinks: true });
  return destinations;
}

/** This validates authored review evidence; it does not perform or imply a review. */
export async function assembleDiscoveries(
  manifestValue: unknown,
  revision: string,
  read: (path: string) => Promise<Uint8Array>,
): Promise<DiscoveryExport> {
  if (!/^[a-f0-9]{40}$/u.test(revision)) throw new Error("Source revision must be an exact Git commit");
  const manifest = object(manifestValue, ["schemaVersion", "figures", "articles"], "manifest");
  if (manifest.schemaVersion !== 1) throw new Error("Unsupported discovery manifest");
  const names = list(manifest.figures, "figures", 128).map((value) => {
    const name = string(value, "figure", 140);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*\.svg$/u.test(name)) throw new Error("Invalid figure filename");
    return name;
  });
  unique(names, "figures");
  const articles: PublishedDiscovery[] = [];
  const destinations = new Map<string, MarkdownDestination[]>();
  for (const value of list(manifest.articles, "articles", 128, 1)) {
    const item = object(value, ARTICLE_KEYS, "article");
    const articleSlug = slug(item.slug, "article slug");
    for (const key of ["title", "description", "topic", "claimScope"]) string(item[key], key, key === "title" ? 180 : 1200);
    const published = date(item.date, "date");
    const updated = date(item.updated, "updated");
    if (updated < published) throw new Error("Article update precedes publication");
    if (item.bodyFile !== "articles/" + articleSlug + ".md") throw new Error("Body path must match its slug");
    const body = new TextDecoder("utf-8", { fatal: true }).decode(await read("discoveries/" + String(item.bodyFile)));
    string(body, "article body", 80_000);
    destinations.set(articleSlug, markdownDestinations(body));
    const citations = list(item.citations, "citations", 64, 1).map((entry) => {
      const citation = object(entry, ["id", "title", "authors", "year", "url", "detail"], "citation");
      for (const key of ["title", "authors", "year", "detail"]) string(citation[key], "citation " + key);
      slug(citation.id, "citation id");
      https(citation.url, "citation URL");
      return citation;
    });
    const citationIds = citations.map((entry) => String(entry.id));
    unique(citationIds, "citation IDs");
    const usedCitations = [...body.matchAll(/\[\^([a-z0-9-]+)\]/gu)].map((match) => match[1]!);
    if (usedCitations.some((id) => !citationIds.includes(id))
      || citationIds.some((id) => !usedCitations.includes(id))) throw new Error("Citations must be used and resolved");
    for (const entry of list(item.artifacts, "artifacts", 32, 1)) {
      const artifact = object(entry, ["label", "url", "kind"], "artifact");
      string(artifact.label, "artifact label", 200);
      string(artifact.kind, "artifact kind", 60);
      https(artifact.url, "artifact URL");
    }
    const related = list(item.relatedSlugs, "relatedSlugs", 8).map((entry) => slug(entry, "related slug"));
    unique(related, "related slugs");
    if (related.includes(articleSlug)) throw new Error("Article cannot relate to itself");
    const provenance = object(item.provenance, ["author", "method", "reviewer", "reviewType", "reviewedAt"], "provenance");
    for (const key of ["author", "method", "reviewer", "reviewType"]) string(provenance[key], key);
    if (provenance.author !== "Hraness" || !/\bAI\b/iu.test(String(provenance.reviewType))) throw new Error("Disclose Hraness authorship and AI review");
    const reviewedAt = date(provenance.reviewedAt, "review date");
    if (reviewedAt < updated) throw new Error("Review must cover the current update");
    const admission = object(item.admission, ["owner", "readerJob", "nonObviousAnswer", "originalContribution", "hostFit", "overlap", "reasonToKeep", "reviewedAt", "reassessOn", "scores"], "admission");
    for (const key of ["owner", "readerJob", "nonObviousAnswer", "originalContribution", "hostFit", "overlap", "reasonToKeep"]) string(admission[key], key);
    if (date(admission.reviewedAt, "admission review date") !== reviewedAt) throw new Error("Review dates disagree");
    const reassessOn = date(admission.reassessOn, "reassessment date");
    const days = (Date.parse(reassessOn) - Date.parse(reviewedAt)) / 86_400_000;
    if (days < 28 || days > 56) throw new Error("Reassessment must be scheduled 28–56 days after review");
    const scores = object(admission.scores, SCORES, "scores");
    if (SCORES.some((key) => scores[key] !== 1 && scores[key] !== 2)
      || SCORES.reduce((sum, key) => sum + Number(scores[key]), 0) < 9) throw new Error("Article has not met the editorial admission threshold");
    const { bodyFile: _bodyFile, ...metadata } = item;
    articles.push({ ...metadata, slug: articleSlug, bodyMarkdown: body });
  }
  const slugs = articles.map((article) => article.slug);
  unique(slugs, "article slugs");
  const usedFigures = new Set<string>();
  for (const article of articles) {
    for (const related of article.relatedSlugs as string[]) if (!slugs.includes(related)) throw new Error("Related article is missing: " + related);
    for (const { kind, target } of destinations.get(article.slug)!) {
      if (target.startsWith("/discoveries/figures/") && kind === "image") {
        const name = target.slice("/discoveries/figures/".length);
        if (!names.includes(name)) throw new Error("Unregistered figure: " + name);
        usedFigures.add(name);
      } else if (target.startsWith("/discoveries/") && kind === "link") {
        if (!slugs.includes(target.slice("/discoveries/".length))) throw new Error("Missing article link: " + target);
      } else if (kind === "link") {
        https(target, "article link");
      } else throw new Error("Figures must be registered local SVG files");
    }
  }
  if (names.some((name) => !usedFigures.has(name))) throw new Error("Remove unused figures from the manifest");
  const figures: DiscoveryExport["figures"] = [];
  for (const name of names) {
    const bytes = await read("discoveries/figures/" + name);
    const svg = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    if (bytes.length > 200_000 || !svg.startsWith("<svg ") || !svg.includes("<title ")
      || /<(?:script|foreignObject|iframe|image|use)\b|\bon[a-z]+\s*=|(?:href|src)\s*=|<!DOCTYPE|<!ENTITY/iu.test(svg)) throw new Error("Unsafe or inaccessible figure: " + name);
    staticSvg(svg);
    figures.push({ name, bytes, sha256: createHash("sha256").update(bytes).digest("hex") });
  }
  return { bundle: { schemaVersion: 1, source: { repository: REPOSITORY, revision }, articles }, figures };
}

async function readBounded(stream: ReadableStream<Uint8Array>, limit: number): Promise<Uint8Array> {
  const reader = stream.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const item = await reader.read();
      if (item.done) break;
      size += item.value.byteLength;
      if (size > limit) throw new Error("Git output exceeded publication bound");
      chunks.push(item.value);
    }
  } finally { await reader.cancel(); }
  return Buffer.concat(chunks);
}

async function gitBytes(root: string, args: string[]): Promise<Uint8Array> {
  const child = Bun.spawn(["git", "-C", root, ...args], { stdin: "ignore", stdout: "pipe", stderr: "pipe" });
  const bounded = (stream: ReadableStream<Uint8Array>, limit: number) => readBounded(stream, limit).catch((error: unknown) => { child.kill(); throw error; });
  const [stdout, stderr, status] = await Promise.allSettled([bounded(child.stdout, 3_000_000), bounded(child.stderr, 32_000), child.exited]);
  if (stdout.status === "rejected") throw stdout.reason;
  if (stderr.status === "rejected") throw stderr.reason;
  if (status.status === "rejected") throw status.reason;
  if (status.value !== 0) throw new Error("Git read failed: " + new TextDecoder().decode(stderr.value).slice(0, 600));
  return stdout.value;
}

export async function gitText(root: string, args: string[]): Promise<string> {
  return new TextDecoder("utf-8", { fatal: true }).decode(await gitBytes(root, args));
}

/** Release export reads only the selected commit, never mixed working-tree bytes. */
export async function exportCommittedDiscoveries(root: string, revision: string): Promise<DiscoveryExport> {
  if (!/^[a-f0-9]{40}$/u.test(revision)) throw new Error("Use an exact source commit");
  const actual = (await gitText(root, ["rev-parse", "--verify", revision + "^{commit}"])).trim();
  if (actual !== revision) throw new Error("Source revision is not a commit");
  const read = async (path: string) => gitBytes(root, ["show", revision + ":" + path]);
  const manifest = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(await read("discoveries/manifest.json"))) as unknown;
  return assembleDiscoveries(manifest, revision, read);
}

/** Local preview only. The CLI forbids writing this uncommitted source to a site. */
export async function previewDiscoveries(root: string, revision: string): Promise<DiscoveryExport> {
  const manifest = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(await readFile(join(root, "discoveries/manifest.json")))) as unknown;
  return assembleDiscoveries(manifest, revision, async (path) => readFile(join(root, path)));
}
