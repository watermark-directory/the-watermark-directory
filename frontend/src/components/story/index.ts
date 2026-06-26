/**
 * The provided story-component library (#724/#731) — the curated vocabulary an MDX chapter
 * body may use. Two mechanisms:
 *
 *  - **Static blocks** (`Callout`, `ChapterDoors`, `Prose`, `Interactive`) + the evidence /
 *    record / figure components are exposed via `STORY_COMPONENTS`, which the rendering shell
 *    (#732) passes as the MDX `components` prop — so chapter bodies write `<Callout>…</Callout>`
 *    with no import.
 *  - **Interactive islands** (DilutionScreen, EntityGraph, …) stay *direct imports* in the MDX,
 *    because their `client:*` directives must be applied at the import site. See `README.md`.
 *
 * Keeping the vocabulary curated (and lint-checkable later, #742) keeps chapters portable
 * across sites: a body composes provided components over feed/site-scoped props, never bespoke
 * per-chapter markup.
 */
import EvidenceTag from "../EvidenceTag.astro";
import FigureStat from "../FigureStat.astro";
import RecordTeardown from "../RecordTeardown.astro";
import WalkTimeline from "../WalkTimeline.astro";
import WithholdingStack from "../WithholdingStack.astro";
import Callout from "./Callout.astro";
import ChapterDoors from "./ChapterDoors.astro";
import Interactive from "./Interactive.astro";
import Prose from "./Prose.astro";
import StoryChapters from "./StoryChapters.astro";

export {
  Callout,
  ChapterDoors,
  Prose,
  Interactive,
  StoryChapters,
  EvidenceTag,
  FigureStat,
  RecordTeardown,
  WalkTimeline,
  WithholdingStack,
};
export type { ChapterDoor } from "./ChapterDoors.astro";

/**
 * The MDX `components` map the shell injects (`<Content components={STORY_COMPONENTS} />`).
 * Names here are usable in any chapter body without an import. Islands are intentionally absent
 * (direct import + client directive).
 */
export const STORY_COMPONENTS = {
  Callout,
  ChapterDoors,
  Prose,
  Interactive,
  StoryChapters,
  EvidenceTag,
  FigureStat,
  RecordTeardown,
  WalkTimeline,
  WithholdingStack,
};
