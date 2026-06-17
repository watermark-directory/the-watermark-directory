---
name: evidentiary-discipline
description: Use whenever a task involves asserting, qualifying, or evaluating factual claims, connections between entities, or the strength of evidence — including drafting investigative prose, reviewing a claim for defensibility, deciding whether something can be published, separating confirmed facts from inferences, or auditing a document for unsupported assertions. Trigger on phrases like "can I say", "is this confirmed", "documented vs inferred", "is this a finding or a question", "no link", or any request to make a claim stronger or punchier.
---

# Evidentiary Discipline

The organizing principle of all investigative work in this project. Every other skill is subordinate to it.

## The two-register rule

Every factual statement falls into exactly one register, and the prose must make clear which:

1. **Confirmed** — supported by a source the author can produce and defend (recorded instrument, filing, dated communication, parcel record, executed agreement, on-record statement, primary document). State it flatly and as fact.
2. **Inferred / open** — supported only by plausibility, timing, proximity, or pattern. Frame it as an explicit question or labeled inference. Never let it read as a finding.

If you cannot place a statement in register 1, it goes in register 2 or it is cut. There is no third option where a strong inference gets to be stated as fact because it is "obviously true."

## Documented vs. inferred connections

A connection between two entities is **documented** only when an instrument ties them: a recorded deed, a filing naming both, a dated communication, a parcel-ownership chain, an executed contract. It is **inferred** when the only ties are:
- name proximity ("both are named in the same article")
- temporal coincidence ("registered the same week")
- geographic adjacency ("the parcel sits next to the facility")
- plausibility ("it would make sense if...")

Inferred connections are legitimate to raise — as questions. They are never legitimate to assert. When in doubt, write the sentence as an interrogative and see whether it survives.

## No-link statements

When the record shows that two entities are *not* connected, say so flatly: "There is no documented relationship between X and Y." Do not hedge a negative finding into mush. A clean no-link statement protects the author's credibility and is itself a result of the work.

## Separate registers stay separate

Distinct investigative threads (e.g. a corridor file, a governance investigation, a procurement thread) are separate registers. Do not import an entity or fact from one thread into another unless an evidentiary bridge — a documented instrument tying them — exists. Filing something "as context" is fine; cross-referencing it as connection is not.

## Self-audit checklist (run before any claim ships)

- Is this register 1 or register 2? Does the sentence make that obvious to the reader?
- If register 1: can the author produce the source on demand?
- If a connection: is it documented or inferred? Is it phrased accordingly?
- If a person's motive/function/relationship: is it sourced, or am I guessing?
- If I'm "strengthening" a claim: am I adding precision, or am I quietly promoting an inference to a finding?
- If negative: did I state it cleanly, or did I hedge a clean no into a maybe?

## When asked to make something punchier

Punch comes from precision and from well-placed questions, never from overstatement. The strongest move is often to state exactly what is confirmed, then ask the one question the confirmed facts cannot themselves answer — and stop. Resist the pull to close the gap for the reader.

## Project enrichment

In this repo the two registers are encoded as the published tag vocabulary — `[verified]` for register 1, `[inference]` / `[open]` for register 2, `[reference]` for an outside-published spec. The project enrichment layer (`docs/investigative-method/ENRICHMENT.md`) binds this skill to that vocabulary, the corpus chain-of-custody rules, and the current corpus-completeness audit. Bind to those; keep this file convention-free.
