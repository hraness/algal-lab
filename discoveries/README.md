# Discoveries

The plain-language accounts of Algal Lab's results are published at [hraness.com/discoveries](https://hraness.com/discoveries). This directory owns their text, references, figures, and editorial review records. The papers, exact certificates, and experiment sources remain in their existing repository locations.

Start with the result and its meaning for a reader without specialist training. Explain how it was found and checked before introducing notation. End with a brief recap of the result and method, and links to the resulting papers, code, and related questions. Group papers that answer the same reader question. A stronger bound or correction usually updates that account instead of creating another page.

## Update an account

1. Preserve the supported result in a proof, certificate, or reproducible record. Resolve an independent review of those exact sources. Keep heuristic observations, finite verified cases, general theorems, and historical novelty distinct.
2. Edit `articles/<slug>.md` and the matching entry in `manifest.json`. References use `[^id]`; each ID needs one matching citation record with its exact title, authors, version or year, link, and useful theorem or section detail. Use immutable artifact links.
3. Add an explanatory SVG under `figures/` when it helps the argument, and register it in the manifest. Use accessible descriptions and captions that distinguish a proved optimum, a bound, and an observed value. Active SVG content and raw HTML are rejected.
4. Record the owner, reader question, original observations, source-check date, scores, named reviewer and reviewer type, review date, and reassessment date. Identify independent AI review as AI review. The validator checks consistency; it cannot perform the review.
5. Run the focused checks and a local preview:

   ```sh
   bun test src/publication/discoveries.test.ts
   bun run discoveries:export --preview --out runs/discoveries-preview
   ```

6. Inspect the rendered article on wide and narrow screens. Resolve mathematical, editorial, accessibility, and layout findings. Complete the repository's required gate and merge through its normal delivery workflow.

The manifest has one entry per article, unique routes, explicit related articles, and an inventory of used figures. Keep the current update covered by its review and schedule reassessment 28 to 56 days later. The website enforces its own publication rules as well.

## Publish the committed version

With a checkout of `hraness/jungle` that contains the Discoveries renderer, export the exact reviewed Algal Lab commit:

```sh
bun run discoveries:export --revision FULL_COMMIT_SHA --out runs/discoveries-publication --site-root /path/to/jungle
```

The command reads the manifest, articles, and figures from that Git commit. Uncommitted edits do not enter a publication export. It checks the destination repository and website package, then updates only `projects/hraness/app/discoveries/content.generated.json` and the named files under `projects/hraness/public/discoveries/figures/`. `export.json` records the source revision and output hashes. A preview cannot install into the website.

Inspect the website diff and run its required validation, including rendered-page checks. Deliver through Jungle's documented local merge queue and verify the production revision and public URLs. Preserve immutable paper releases. Do not hand-edit the generated website bundle or let a provider response write a public article.

Future `$algal-discovery` sessions follow this path after each supported result. The [portable loop](../docs/discovery-loop.md) controls experiments; the outer agent owns scientific review, literature comparison, article maintenance, and repository delivery.
