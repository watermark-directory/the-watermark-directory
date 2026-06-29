# Writing a story chapter

A site's *story* (#724) is authored as data: one MDX file per chapter under
`src/content/stories/<site>/<codename>/<slug>.mdx`. The **frontmatter** is the chapter spine
(validated by `STORY_CHAPTER_SCHEMA` in `src/content.config.ts`); the **body** is the prose,
composed from the provided components in this directory. The rendering shell (the
`stories/[codename]/[chapter]` route, #732) wraps the body with the wayfinding, eyebrow, title,
and chapter nav — so a chapter body is *just the content*, never the chrome.

## Frontmatter (the spine)

```yaml
---
step: 4                       # 1-based reading position
slug: water                   # must match the filename
title: "What it does to the water"
skill: "Reading an NPDES permit · the 7Q10 low-flow screen"
anchor: "NPDES dilution + the cooling-draw screen"   # human description of what it tears down
anchorRecordRels:             # library record rels → the "↩ seen in the walk" backlinks
  - oepa/oepa-2PH00006-american-ii-fact-sheet.npdes.yaml
live: true                    # false ⇒ drafting (wayfinding gates its go-links)
# eyebrow: "Chapter 4"        # optional override; defaults to "Chapter <step>"
---
```

## The provided components

These are injected as the MDX `components` map (`STORY_COMPONENTS`), so use them in the body
**without importing**. They reuse the site's existing styles — stay within this vocabulary so
chapters remain portable across sites and on-brand (watermark-design).

| Component | Use |
|---|---|
| `<Prose>…</Prose>` | a run of readable prose at the chapter measure |
| `<Interactive heading="…">…</Interactive>` | a full-bleed section around a table or island |
| `<Callout title="…" variant="default\|takeaway\|open">…</Callout>` | a boxed aside / key point |
| `<ChapterDoors doors={[{ label, blurb, path }]} />` | the "Explore this in the library" grid (paths are site-relative) |
| `<RecordTeardown record={…} />` | a primary-source teardown |
| `<EvidenceTag kind="verified\|inference\|open">…</EvidenceTag>` | an inline evidence pill |
| `<FigureStat stat={…} />` | one figure treatment (grounded vs modeled vs withheld) |

Markdown is rendered as prose by default, so short passages need no wrapper — reach for
`<Prose>` when you're interleaving prose with full-bleed `<Interactive>` blocks.

## Interactive islands

Islands (`DilutionScreen`, `EntityGraph`, `MoneyFlow`, …) are **imported directly** in the MDX,
because their `client:*` directive must be applied at the import site:

```mdx
import DilutionScreen from "../../../../components/islands/DilutionScreen.tsx";

<Interactive heading="What the campus takes out of the basin">
  <DilutionScreen client:only="react" data={dilution} />
</Interactive>
```

Island **data comes from the per-site bundle** (`buildDilution()` etc., #728/#739) — never a
hardcoded site value. A chapter that reads its figures from the feeds works for any site that
hosts the story.

## Discipline

The story is held to the same evidence grammar as the rest of the record: every figure carries
its confidence (`[verified]` / `[inference]` / `[open]`), inference is labelled and never dressed
as fact, and each claim cites its source. See the investigative-method skills.
