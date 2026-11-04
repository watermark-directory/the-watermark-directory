"""The typed-path query engine over the corpus mirror — `query` / `pack` / `estimate` (#2132).

`neighbors` chains edges in both directions and filters on neither relationship nor direction:
it carries both out as labels on the result and reads neither as an input. A server offering
only that has typed its graph and left no way to walk by the types. **This is the walk.**

Three things this module holds that the MCP handlers in :mod:`watermark.agent.yidam_tools`
deliberately do not, because each is a distinction a caller branches on and a shape-passing
implementation would collapse:

* **A rejection is an answer, not an error.** ``rejected`` carries a frozen code and never
  travels as MCP's ``isError``. An empty ``results`` with ``rejected: None`` means the query was
  well formed and the corpus is quiet — and the two MUST be distinguishable, which is the whole
  reason this is not ``retrieve`` with a filter.
* **An absence is not a rejection.** ``rejected`` says the query is wrong; ``absence`` says the
  query is right and the corpus has nothing. Reporting a typo as ``class-unpopulated`` would
  tell a caller its mistake was a true negative.
* **A diagnostic is neither.** A query that *ran* can still report a near miss. Promoting those
  to rejections refuses legal queries.

The grammar is small and whitespace-delimited — ``-rel->`` and ``<-rel-`` are single tokens, so
a path is ``STEP HOP STEP HOP STEP``. A step is a class name or ``*``, optionally narrowed by a
property filter ``[name=value]``, optionally opened by a similarity anchor ``~"text"`` which only
the entry step may carry. A filter is comma-separated predicates (contract 0.30.0): ``=``,
``!=``, ``~``, an ordering (``<`` ``<=`` ``>`` ``>=``, on ``date`` and ``number`` only), the
absence test ``name?``, and the ``>?`` affix that widens one comparison to admit the absent.
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from watermark.site.corpus_mirror import (
    CLASSES,
    ONTOLOGY,
    UNIVERSAL_PROPERTIES,
    Mirror,
    MirrorNode,
    node_text,
    resolve_link_target,
)

#: Every projectable field name. ``properties.<name>`` is handled separately.
SELECTABLE = ("node", "class", "label", "description", "body")

#: The default projection — enough to identify a node and no prose.
DEFAULT_SELECT = "node,class,label"

#: Rejection codes, frozen by the contract. A client branches on these.
#:
#: **These are the names a server ANSWERS with** (contract 0.15.0). Until then the list held
#: three lint check ids — ``unknown-property``, ``unlicensed-edge``, ``edge-target-class`` — that
#: no reference rejection ever carried, so a client branching on the frozen set had arms that
#: could not be taken. ``anchor-across`` is the one BOSC can reach only by asking for it:
#: ``across`` with an anchored entry. The contract freezes ``anchor-at-revision`` and
#: ``history-unreadable`` OUT, because no MCP call names a revision.
REJECTION_CODES = (
    "parse",
    "unknown-class",
    "undeclared-property",
    "unordered-property",
    "unsatisfiable-predicate",
    "unlicensed-hop",
    "unknown-field",
    "anchor-not-entry",
    "anchor-unavailable",
    "anchor-unresolvable",
    "anchor-across",
)

#: Diagnostic codes, frozen too (contract 0.18.0) — a query that RAN, and a near miss worth
#: saying. ``corpus-excluded`` needs an installed dependency, which BOSC does not pin.
DIAGNOSTIC_CODES = (
    "trivial-predicate",
    "undeclared-relationship",
    "narrowed",
    "corpus-excluded",
)

#: The only declared types with an order. Anything else — a coined type included — refuses an
#: ordering with ``unordered-property`` rather than comparing text, which reads ``10`` before ``9``.
ORDERED_TYPES = ("date", "number")

#: The claim vocabulary a `type: claim` property can hold, bracketed or bare.
CLAIM_STANDINGS = ("verified", "inference", "open")

#: Absence codes, frozen by the contract. Three about the entry step, four about a hop, one
#: fallback. ``relationship-unauthored`` is the one worth the most — a relationship a class
#: licenses and no instance uses is invisible from every other angle, and comes back from a
#: traversal exactly as a mistyped name would.
ABSENCE_CODES = (
    "class-unpopulated",
    "predicate-unsatisfied",
    "anchor-empty",
    "relationship-unauthored",
    "relationship-unknown",
    "no-edge-from-here",
    "edge-lands-elsewhere",
    "no-match",
)

_STEP_RE = re.compile(
    r"""^
    (?P<cls>\*|[A-Za-z][A-Za-z0-9_-]*)          # a class name, or the wildcard
    (?:\[(?P<pred>[^\]]*)\])?                   # optional property predicate
    (?:~"(?P<anchor>[^"]*)")?                   # optional similarity anchor
    $""",
    re.X,
)
_FORWARD_RE = re.compile(r"^-(?P<rel>[^>\s]+)->$")
_BACKWARD_RE = re.compile(r"^<-(?P<rel>[^>\s]+)-$")


#: Operators in the order they are recognised. Two-character ones first, so `<=` is not read as
#: `<` followed by a value starting `=`.
_OPERATORS = ("!=", "<=", ">=", "<", ">", "?", "=", "~")
ORDERINGS = ("<", "<=", ">", ">=")


@dataclass(frozen=True)
class Predicate:
    """One property test inside a step's brackets.

    ``op`` is one of ``=``, ``!=``, ``~``, ``<``, ``<=``, ``>``, ``>=`` or ``?``. ``?`` IS the
    absence test and takes no operand; ``or_absent`` is the AFFIX (``ended>?1893``) that widens
    one comparison to admit a node that does not carry the property. They are not spellings of
    each other, which is why neither is modelled as the other.
    """

    name: str
    op: str
    value: str = ""
    or_absent: bool = False

    def text(self) -> str:
        if self.op == "?":
            return f"{self.name}?"
        return f"{self.name}{self.op}{'?' if self.or_absent else ''}{self.value}"


@dataclass(frozen=True)
class Step:
    """One step of a path: where to stand, and (after the first) how we got here."""

    node_class: str  # a class name, or "*"
    predicates: tuple[Predicate, ...] = ()
    anchor: str | None = None
    relationship: str | None = None  # None on the entry step
    direction: str = "out"  # "out" follows an authored edge, "in" follows it backwards


@dataclass(frozen=True)
class Rejection:
    """The query is wrong. Never an ``isError`` — the caller branches on ``code``."""

    step: int
    code: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"step": self.step, "code": self.code, "message": self.message}


@dataclass(frozen=True)
class Diagnostic:
    """The query RAN and something about it is worth saying."""

    level: str
    step: int
    code: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "step": self.step,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class Absence:
    """The query is right and the corpus is quiet — with the reason, derived not inferred.

    ``instances`` is the denominator the message is about: instances of the step's class at an
    entry step, nodes that reached the previous step at a hop. *None of three* and *none of nine
    hundred* are different facts about a corpus.
    """

    step: int
    code: str
    message: str
    instances: int
    elsewhere: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "code": self.code,
            "message": self.message,
            "instances": self.instances,
            # Always present, empty when there is nothing to name, so a client never has to
            # distinguish "no dependency holds this" from "the server did not look".
            "elsewhere": list(self.elsewhere),
        }


@dataclass
class Cost:
    """What the CALLER pays, not what the server did.

    ``nodes_read`` counts nodes whose content was evaluated by a predicate, tested for a hop's
    class, or projected — never the corpus load, which happens either way. Class narrowing is a
    directory listing and is not charged; a degraded keyword anchor **is** charged for every
    candidate it scored, because it read them. Counted as distinct nodes: a node evaluated twice
    costs a caller its content once.
    """

    steps: int = 0
    edges_walked: int = 0
    corpus_nodes: int = 0
    chars: int = 0
    _read: set[str] = field(default_factory=set)

    def read(self, node_ids: Any) -> None:
        self._read.update(node_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "edges_walked": self.edges_walked,
            "nodes_read": len(self._read),
            "chars": self.chars,
            # `chars / 4`, an approximation by construction and not a tokenizer. There is
            # deliberately no range: a caller holding a real tokenizer needs the exact `chars`
            # rather than a wider guess laid over it.
            "tokens": self.chars // 4,
            "corpus_nodes": self.corpus_nodes,
        }


@dataclass
class Execution:
    """A parsed, typechecked, executed path — everything the three tools render from."""

    query: str
    steps: tuple[Step, ...] = ()
    #: What each step's class resolved to — a `*` narrowed by a predicate reports the classes
    #: that declare it, which is the difference between "every class" and "the one that does".
    step_classes: tuple[tuple[str, ...], ...] = ()
    rejected: Rejection | None = None
    absence: Absence | None = None
    anchor: dict[str, Any] | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    matched: list[MirrorNode] = field(default_factory=list)
    at: int = 0
    cost: Cost = field(default_factory=Cost)


# --- the ontology, read as data ---------------------------------------------------------------
# From `ONTOLOGY` directly, never by parsing the emitted `.ont.yml` back. A second reader would
# be a second ontology, and the two would drift the way the report replica did (#2051).
def declared_properties(node_class: str) -> dict[str, str]:
    """``{name: type}`` a class declares, plus the corpus-wide universal ones."""
    out = {p.name: p.type for p in UNIVERSAL_PROPERTIES}
    if (ont := ONTOLOGY.get(node_class)) is not None:
        out.update({p.name: p.type for p in ont.properties})
    return out


def licensed_edges(node_class: str) -> list[dict[str, str]]:
    """Every edge ``node_class`` is party to, **from both ends**.

    An edge is documented from both sides: the class that authors it declares `direction: out`,
    and the class it lands on is party to the same relationship inbound. The licensing check
    ignores direction, so filtering to `out` here would answer a question the gate does not ask.
    """
    out: list[dict[str, str]] = []
    for owner, ont in ONTOLOGY.items():
        for edge in ont.edges:
            if owner == node_class:
                out.append(
                    {
                        "relationship": edge.relationship,
                        "target": edge.target,
                        "direction": "out",
                        "description": edge.description,
                    }
                )
            elif edge.target == node_class:
                out.append(
                    {
                        "relationship": edge.relationship,
                        "target": owner,
                        "direction": "in",
                        "description": edge.description,
                    }
                )
    return out


def _edge_spec(source_class: str, relationship: str, direction: str) -> tuple[str, str] | None:
    """``(owner, target)`` for a licensed hop, or ``None`` when no class licenses it that way."""
    for owner, ont in ONTOLOGY.items():
        for edge in ont.edges:
            if edge.relationship != relationship:
                continue
            if direction == "out" and owner == source_class:
                return owner, edge.target
            if direction == "in" and edge.target == source_class:
                return owner, owner
    return None


def _near_miss(name: str, candidates: Any) -> str | None:
    """The closest candidate within one edit — what makes a rejection actionable."""
    import difflib

    hit = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.6)
    return hit[0] if hit else None


# --- parsing ----------------------------------------------------------------------------------
#: Whitespace splits a path — except inside an anchor's quotes. `concept~"water quality"` is one
#: token and two words, and splitting it on the space rejected a legal query as malformed.
_TOKEN_RE = re.compile(r'[^\s"]*"[^"]*"[^\s"]*|\S+')


def tokenize(query: str) -> list[str]:
    """Split a path on whitespace, keeping a quoted anchor whole."""
    return _TOKEN_RE.findall(query or "")


_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


def _unquote(raw: str) -> str | None:
    if len(raw) >= 2 and raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    return None


def parse_filter(raw: str) -> tuple[tuple[Predicate, ...], str | None]:
    """The predicates a `[...]` holds — comma-separated, commas inside quotes kept.

    One grammar for a step's brackets and for `retrieve`'s ``where``: a predicate that parsed in
    one and not the other would be the surface disagreeing with itself about what a predicate
    is. Returns ``(predicates, None)`` or ``((), message)``.
    """
    parts: list[str] = []
    current, quoted = "", False
    for ch in raw:
        if ch == '"':
            quoted = not quoted
        if ch == "," and not quoted:
            parts.append(current)
            current = ""
            continue
        current += ch
    parts.append(current)

    out: list[Predicate] = []
    for part in (p.strip() for p in parts):
        if not part:
            return (), "an empty predicate between commas"
        # The first operator character wins, so a value may itself contain one.
        at = min((i for i, ch in enumerate(part) if ch in "=!~<>?"), default=None)
        if at is None:
            return (), f"`{part}` is not a predicate — it has no operator"
        name, rest = part[:at].strip(), part[at:]
        op = next((o for o in _OPERATORS if rest.startswith(o)), None)
        if op is None:  # a lone `!`
            return (), f"`!` is not an operator — write `!=` (in `{part}`)"
        if not _IDENT_RE.match(name):
            return (), f"`{name}` is not a property name"
        rest = rest[len(op) :]
        if op == "?":
            if rest.strip():
                return (), (
                    f"`{name}?` tests whether the property is absent and takes no value — for a "
                    "comparison an absent property also satisfies, write the `?` after the "
                    f"operator, as `{name}>?{rest.strip()}`"
                )
            out.append(Predicate(name, "?"))
            continue
        or_absent = rest.startswith("?")
        value = rest[1:] if or_absent else rest
        value = value.strip()
        if not value:
            return (), f"`{part}` has no value"
        unquoted = _unquote(value)
        out.append(Predicate(name, op, unquoted if unquoted is not None else value, or_absent))
    return tuple(out), None


def parse_where(raw: str) -> tuple[tuple[Predicate, ...], Rejection | None]:
    """`retrieve`'s ``where`` — a step's filter with the brackets off (or on; both are taken)."""
    text = (raw or "").strip()
    if not text:
        return (), Rejection(0, "parse", "an empty `where` — write at least one predicate")
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    predicates, problem = parse_filter(text)
    if problem is not None:
        return (), Rejection(0, "parse", problem)
    return predicates, None


def parse(query: str) -> tuple[tuple[Step, ...], Rejection | None]:
    """Split a path into steps, or reject it with ``parse``."""
    tokens = tokenize(query)
    if not tokens:
        return (), Rejection(0, "parse", "empty query — name a class, or `*`, to enter at")

    steps: list[Step] = []
    relationship: str | None = None
    direction = "out"
    for index, token in enumerate(tokens):
        if index % 2 == 0:
            match = _STEP_RE.match(token)
            if match is None:
                return (), Rejection(
                    len(steps),
                    "parse",
                    f"`{token}` is not a step — write a class name, `*`, "
                    '`class[property=value]`, or `class~"text"`',
                )
            predicates: tuple[Predicate, ...] = ()
            if (raw := match.group("pred")) is not None:
                predicates, problem = parse_filter(raw)
                if problem is not None:
                    return (), Rejection(len(steps), "parse", problem)
            steps.append(
                Step(
                    node_class=match.group("cls"),
                    predicates=predicates,
                    anchor=match.group("anchor"),
                    relationship=relationship,
                    direction=direction,
                )
            )
        else:
            if (forward := _FORWARD_RE.match(token)) is not None:
                relationship, direction = forward.group("rel"), "out"
            elif (backward := _BACKWARD_RE.match(token)) is not None:
                relationship, direction = backward.group("rel"), "in"
            else:
                return (), Rejection(
                    len(steps),
                    "parse",
                    f"`{token}` is not a hop — write `-relationship->` or `<-relationship-`, "
                    "with whitespace around it",
                )
    if len(tokens) % 2 == 0:
        return (), Rejection(
            len(steps), "parse", "the path ends on a hop — name the class it lands on"
        )
    return tuple(steps), None


# --- typechecking -----------------------------------------------------------------------------
_DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def parse_date(raw: Any) -> tuple[int, ...] | None:
    """An ISO date at whatever precision it is known to — ``YYYY``, ``YYYY-MM``, ``YYYY-MM-DD``.

    Structural, not a calendar: what this refuses is prose in a date field, never reduced
    precision, because a year is the precision many facts are actually known to.
    """
    match = _DATE_RE.match(str(raw).strip())
    if match is None:
        return None
    return tuple(int(g) for g in match.groups() if g is not None)


def parse_number(raw: Any) -> float | None:
    if isinstance(raw, bool):
        return None
    try:
        value = float(str(raw).strip())
    except ValueError:
        return None
    return value if value == value and value not in (float("inf"), float("-inf")) else None


def _value_problem(declared: str, value: str) -> str | None:
    """Why a property of type ``declared`` could never hold ``value`` — or ``None``."""
    if declared == "date" and parse_date(value) is None:
        return f"`{value}` is not a date — write `YYYY-MM-DD`, or `YYYY-MM` or `YYYY`"
    if declared == "number" and parse_number(value) is None:
        return f"`{value}` is not a number"
    if declared == "claim" and value.strip().strip("[]") not in CLAIM_STANDINGS:
        return f"`{value}` is not a claim tag — a claim holds one of {', '.join(CLAIM_STANDINGS)}"
    if declared in ("list", "mapping"):
        return f"a `{declared}` property is not a single value"
    return None


def _ask(
    node_class: str, index: int, pred: Predicate
) -> tuple[Rejection | None, Diagnostic | None]:
    """Whether ``pred`` can be ASKED of ``node_class`` — a rejection, or a warning, or neither.

    Asked of, not merely declared by: a class declaring `date` as `string` declares it and still
    cannot be asked `date<1900`, which is why `*` narrows on this and not on declaration alone.
    """
    declared = declared_properties(node_class).get(pred.name)
    if declared is None:
        return Rejection(
            index, "undeclared-property", f"`{node_class}` does not declare `{pred.name}`"
        ), None
    if pred.op == "?":
        return None, None
    if pred.op in ORDERINGS and declared not in ORDERED_TYPES:
        return (
            Rejection(
                index,
                "unordered-property",
                f"`{pred.name}` is `type: {declared}` on `{node_class}`, and `{pred.op}` is "
                "defined on `date` and `number` only — comparing anything else would be a "
                "comparison of text, which reads `10` as before `9`. Use `=`, `!=` or `~`.",
            ),
            None,
        )
    if declared in ("list", "mapping") and pred.op in ("=", "~"):
        return (
            Rejection(
                index,
                "unsatisfiable-predicate",
                f"`{pred.name}` is `type: {declared}` on `{node_class}`, and a query does not "
                f"read inside a {declared} — `{pred.op}` would match nothing. Use "
                f"`{pred.name}?`.",
            ),
            None,
        )
    if pred.op == "~":
        return None, None  # substring over text: a fragment need not be a legal value
    problem = _value_problem(declared, pred.value)
    if problem is None:
        return None, None
    if pred.op == "!=":
        return None, Diagnostic(
            "warn",
            index,
            "trivial-predicate",
            f"`{pred.text()}` is true of every `{node_class}` that carries the property: {problem}",
        )
    return (
        Rejection(
            index,
            "unsatisfiable-predicate",
            f"`{pred.name}` cannot hold that value: {problem}",
        ),
        None,
    )


def _narrow(step: Step, index: int) -> tuple[tuple[str, ...], Rejection | None, list[Diagnostic]]:
    """The classes a step stands on once its predicates are asked of each candidate."""
    if step.node_class != "*":
        candidates: tuple[str, ...] = (step.node_class,)
    else:
        candidates = tuple(CLASSES)
    if not step.predicates:
        return candidates, None, []
    for pred in step.predicates:
        if not any(pred.name in declared_properties(c) for c in candidates):
            # Over EVERY candidate, not `candidates[0]`: the rejection was decided across all of
            # them, so drawing the hint from one arbitrary class hides a later class's near miss.
            near = _near_miss(pred.name, {p for c in candidates for p in declared_properties(c)})
            return (
                (),
                Rejection(
                    index,
                    "undeclared-property",
                    f"no class declares `{pred.name}`"
                    + (f" — did you mean `{near}`?" if near else ""),
                ),
                [],
            )
    kept: list[str] = []
    first: Rejection | None = None
    warnings: dict[str, Diagnostic] = {}
    for node_class in candidates:
        refused: Rejection | None = None
        for pred in step.predicates:
            rejection, warning = _ask(node_class, index, pred)
            if rejection is not None:
                refused = rejection
                break
            if warning is not None:
                warnings.setdefault(pred.text(), warning)
        if refused is None:
            kept.append(node_class)
        elif first is None or first.code == "undeclared-property":
            # A class that does not declare the property is the least informative refusal
            # when another declares it and cannot be asked — say the more specific one.
            first = refused
    if not kept:
        assert first is not None
        return (), first, []
    diagnostics = list(warnings.values())
    if step.node_class == "*" and len(kept) < len(candidates):
        skipped = [c for c in candidates if c not in kept]
        diagnostics.insert(
            0,
            Diagnostic(
                "info",
                index,
                "narrowed",
                f"`*` narrowed to the classes `{', '.join(p.text() for p in step.predicates)}` "
                f"can be asked of: {', '.join(kept)} (skipped: {', '.join(skipped)})",
            ),
        )
    return tuple(kept), None, diagnostics


def step_classes(steps: tuple[Step, ...]) -> tuple[tuple[str, ...], ...]:
    """The classes each step actually stands on, after a `*` is narrowed by its predicates."""
    return tuple(_narrow(step, i)[0] for i, step in enumerate(steps))


def typecheck(steps: tuple[Step, ...]) -> tuple[Rejection | None, list[Diagnostic]]:
    """Reject a path the ontology cannot license, and report what it can only warn about.

    Without an ontology every class name and every relationship is accepted, so a misspelling
    comes back as zero results — the one failure this tool exists to prevent.
    """
    diagnostics: list[Diagnostic] = []
    for index, step in enumerate(steps):
        if step.anchor is not None and index > 0:
            return (
                Rejection(
                    index,
                    "anchor-not-entry",
                    "only the entry step may open on a similarity anchor; a later `~` is not a "
                    "filter and is refused rather than reinterpreted as one",
                ),
                diagnostics,
            )
        if step.node_class != "*" and step.node_class not in CLASSES:
            near = _near_miss(step.node_class, CLASSES)
            return (
                Rejection(
                    index,
                    "unknown-class",
                    f"no class `{step.node_class}`"
                    + (f" — did you mean `{near}`?" if near else "")
                    + f" (declared: {', '.join(CLASSES)})",
                ),
                diagnostics,
            )
        _, rejection, step_diagnostics = _narrow(step, index)
        if rejection is not None:
            return rejection, diagnostics
        diagnostics.extend(step_diagnostics)
        if step.relationship is None:
            continue
        # A hop is reported at the step it LEAVES — upstream's `steps[i].hop` is the edge out of
        # step i, and both its rejection and its diagnostic name that index. An absence is the
        # other way round (the step the walk failed to reach), and stays so.
        hop_at = index - 1
        source = steps[index - 1].node_class
        sources = CLASSES if source == "*" else (source,)
        licensed = [c for c in sources if _edge_spec(c, step.relationship, step.direction)]
        if not licensed:
            every = {e.relationship for ont in ONTOLOGY.values() for e in ont.edges}
            near = _near_miss(step.relationship, every)
            hint = f" — did you mean `{near}`?" if near else ""
            direction = "outbound" if step.direction == "out" else "inbound"
            # **A non-empty `edges:` says these relationships exist, not "and no others may."**
            # Only `exhaustive` closes the vocabulary; under any other policy an undeclared
            # relationship is a DIAGNOSTIC on a query that runs. Reading every declaration as
            # exhaustive put 210 errors on a compliant corpus upstream, and a server that
            # rejects here refuses legal queries against every corpus written before the field
            # existed. BOSC declares `exhaustive` on all five classes — truthfully, because its
            # mirror is generated — so it takes the rejecting arm; the other is the contract's
            # and is exercised in the tests.
            closed = all(ONTOLOGY[c].edge_policy == "exhaustive" for c in sources if c in ONTOLOGY)
            if closed:
                return (
                    Rejection(
                        hop_at,
                        "unlicensed-hop",
                        f"`{source}` does not license `{step.relationship}` {direction}{hint}",
                    ),
                    diagnostics,
                )
            diagnostics.append(
                Diagnostic(
                    "warn",
                    hop_at,
                    "undeclared-relationship",
                    f"`{source}` does not declare `{step.relationship}` {direction}{hint}; its "
                    "edge policy is not exhaustive, so the query runs",
                )
            )
            continue
        if step.node_class != "*":
            targets = {
                spec[1]
                for c in licensed
                if (spec := _edge_spec(c, step.relationship, step.direction))
            }
            if step.node_class not in targets:
                return (
                    Rejection(
                        hop_at,
                        "unlicensed-hop",
                        f"`{step.relationship}` lands on {', '.join(sorted(targets))}, "
                        f"not on `{step.node_class}`",
                    ),
                    diagnostics,
                )
    return None, diagnostics


# --- execution --------------------------------------------------------------------------------
def _property_of(node: MirrorNode, name: str) -> Any:
    return node.meta.get(name)


def _scalars(raw: Any) -> list[str]:
    """A property's values as text — one per list element; absent, ``null`` and ``[]`` alike
    yield none, which is what makes the three ONE absence condition rather than three."""
    if raw is None or isinstance(raw, dict):
        return []
    if isinstance(raw, list):
        return [v for item in raw for v in _scalars(item)]
    return [str(raw)]


def _compare_dates(stored: str, operand: str) -> int | None:
    """Compare at the precision the two sides SHARE — ``1893-04-01 < 1900`` is decided on the
    years. Dropping both to the coarser is what lets ``began>=1893-06-01`` return a row that
    knows only ``1893`` instead of silently undercounting."""
    left, right = parse_date(stored), parse_date(operand)
    if left is None or right is None:
        return None
    shared = min(len(left), len(right))
    a, b = left[:shared], right[:shared]
    return (a > b) - (a < b)


def _compare_numbers(stored: str, operand: str) -> int | None:
    left, right = parse_number(stored), parse_number(operand)
    if left is None or right is None:
        return None
    return (left > right) - (left < right)


def _holds(values: list[str], pred: Predicate, declared: str | None) -> bool:
    """Whether a node's values satisfy one predicate.

    Absence satisfies NO operator — ``!=`` included — unless the predicate is the absence test
    itself or carries the ``>?`` affix. A stored value that is not a date (or not a number)
    orders against nothing: guessing for it would be the undercount's louder twin.
    """
    if not values:
        return pred.op == "?" or pred.or_absent
    if pred.op == "?":
        return False
    claim = declared == "claim"
    numeric = declared == "number"
    dated = declared == "date"

    def norm(v: str) -> str:
        # A `type: claim` value is written `[open]` here and `open` upstream; both are the same
        # standing, so `claim_tag=open` matches either spelling.
        return v.strip().strip("[]") if claim else v

    wanted = norm(pred.value)

    def equal(v: str) -> bool:
        if numeric:
            return _compare_numbers(v, pred.value) == 0
        v = norm(v)
        # `=` compares at the precision the QUERY wrote: `observed_on=2026-08` matches every day
        # in that month, and `began=1893-04-01` does not match `began: 1893`.
        return v == wanted or (dated and v.startswith(wanted + "-"))

    def one(v: str) -> bool:
        if pred.op == "=":
            return equal(v)
        if pred.op == "!=":
            return not equal(v)
        if pred.op == "~":
            return pred.value.lower() in v.lower()
        order = _compare_numbers(v, pred.value) if numeric else _compare_dates(v, pred.value)
        if order is None:
            return False
        return {"<": order < 0, "<=": order <= 0, ">": order > 0, ">=": order >= 0}[pred.op]

    # `!=` has to hold of every element, or `[open, verified]` would satisfy `!= open`.
    return all(one(v) for v in values) if pred.op == "!=" else any(one(v) for v in values)


def satisfies(node: MirrorNode, predicates: tuple[Predicate, ...]) -> bool:
    """Whether a node satisfies every predicate, each read at the type its class declares."""
    declared = declared_properties(node.node_class)
    return all(
        _holds(_scalars(_property_of(node, p.name)), p, declared.get(p.name)) for p in predicates
    )


def _keyword_entries(
    mirror: Mirror, node_classes: tuple[str, ...], text: str, k: int
) -> list[MirrorNode]:
    """The degraded anchor: term-overlap over the entry step's instances, best first.

    Takes the step's RESOLVED classes, not its written one. `*[rel=owns]~"water"` narrows to the
    classes that declare `rel` before the anchor runs, so the anchor scores that pool and no
    other — otherwise it both leaks out-of-class nodes into `anchor.entries` and scores far more
    candidates than `cost` is charged for.
    """
    terms = [t for t in re.split(r"\s+", text.lower().strip()) if t]
    if not terms:
        return []
    pool = [n for n in mirror.nodes if n.node_class in node_classes]
    scored = []
    for node in pool:
        haystack = node_text(node).lower()
        hits = sum(1 for t in terms if t in haystack)
        if hits:
            scored.append((hits / len(terms), node))
    scored.sort(key=lambda s: (-s[0], s[1].id))
    return [node for _, node in scored[:k]]


def _edges(mirror: Mirror) -> list[tuple[str, str, str]]:
    """Every ``(from_id, to_id, relationship)``, targets resolved to node ids."""
    return [
        (node.id, resolve_link_target(node.node_class, link.target), link.relationship)
        for node in mirror.nodes
        for link in node.links
    ]


def _authored(mirror: Mirror, relationship: str) -> bool:
    return any(link.relationship == relationship for node in mirror.nodes for link in node.links)


def execute(
    mirror: Mirror,
    query: str,
    *,
    anchor_k: int = 1,
    vector_ready: bool = False,
    across: bool = False,
) -> Execution:
    """Parse, typecheck and walk. Never raises for a bad query — it returns a rejection.

    ``across`` changes nothing about the walk — BOSC installs no dependency, so a spanning run
    reads the same corpus a local one does — except that an ANCHORED spanning query is rejected
    ``anchor-across``, as the CLI rejects it: the vector index is this corpus's, and an anchor
    that entered a foreign corpus through it would rank a dependency's nodes in a space built
    from someone else's text. Asking is enough to be refused; that nothing foreign is installed
    does not make the request coherent.
    """
    run = Execution(query=query)
    run.cost.corpus_nodes = len(mirror.nodes)

    steps, rejection = parse(query)
    if rejection is not None:
        run.rejected = rejection
        return run
    run.steps = steps
    run.step_classes = step_classes(steps)
    run.cost.steps = len(steps)

    rejection, diagnostics = typecheck(steps)
    run.diagnostics = diagnostics
    if rejection is not None:
        run.rejected = rejection
        return run
    if across and steps[0].anchor is not None:
        run.rejected = Rejection(
            0,
            "anchor-across",
            "a similarity anchor cannot open a spanning query: the vector index is this "
            "corpus's, and entering another corpus through it would rank that corpus's nodes "
            "in a space built from this one's text — drop `across` or the `~` anchor",
        )
        return run

    by_id = {n.id: n for n in mirror.nodes}
    edges = _edges(mirror)

    # --- the entry step ---------------------------------------------------------------------
    entry = steps[0]
    entry_classes = run.step_classes[0]
    pool = [n for n in mirror.nodes if n.node_class in entry_classes]
    if entry.anchor is not None:
        # `degraded` lives on the anchor, never at the top level: a query with no anchor
        # performed no retrieval, and a `false` up there would read as retrieval succeeding.
        entries = _keyword_entries(mirror, entry_classes, entry.anchor, max(1, anchor_k))
        # `pool` IS what the anchor scored — same classes, same nodes. The charge is honest only
        # because those two are built from `entry_classes`; feeding the anchor a wider set would
        # silently under-bill the most expensive step there is.
        run.cost.read(n.id for n in pool)
        run.anchor = {
            "step": 0,
            "text": entry.anchor,
            "k": max(1, anchor_k),
            "degraded": not vector_ready,
            "degraded_reason": None if vector_ready else "no_index",
            "repair": None
            if vector_ready
            else "build the corpus vector index — `mise run corpus-vector-index`",
            "entries": [{"node": n.id, "class": n.node_class, "label": n.label} for n in entries],
        }
        current = entries
        if not current:
            run.absence = Absence(
                0,
                "anchor-empty",
                f"the similarity anchor {entry.anchor!r} resolved to no entry node",
                len(pool),
            )
            return run
    else:
        current = pool
        if not current:
            run.absence = Absence(
                0,
                "class-unpopulated",
                f"the ontology declares `{entry.node_class}` and it holds no instances",
                0,
            )
            return run

    if entry.predicates:
        run.cost.read(n.id for n in current)
        before = len(current)
        current = [n for n in current if satisfies(n, entry.predicates)]
        if not current:
            run.absence = Absence(
                0,
                "predicate-unsatisfied",
                f"`{entry.node_class}` holds instances and none satisfies "
                f"`{','.join(p.text() for p in entry.predicates)}`",
                before,
            )
            return run

    # --- the hops ---------------------------------------------------------------------------
    for index, step in enumerate(steps[1:], start=1):
        run.at = index
        assert step.relationship is not None
        reached = len(current)
        here = {n.id for n in current}
        if step.direction == "out":
            landed = [to for (frm, to, rel) in edges if rel == step.relationship and frm in here]
        else:
            landed = [frm for (frm, to, rel) in edges if rel == step.relationship and to in here]
        run.cost.edges_walked += len(landed)

        if not landed:
            # Declared-and-unused and never-heard-of come back from a traversal identically and
            # their repairs are opposite, so they are split. The first is a corpus that has not
            # written what its ontology promises; the second is almost always a typo.
            if not _authored(mirror, step.relationship):
                code, message = (
                    "relationship-unauthored",
                    f"a class declares `{step.relationship}` and no instance authors it",
                )
            else:
                code, message = (
                    "no-edge-from-here",
                    f"`{step.relationship}` is authored elsewhere, by nothing that reached "
                    "the previous step",
                )
            run.absence = Absence(index, code, message, reached)
            return run

        candidates = [by_id[i] for i in dict.fromkeys(landed) if i in by_id]
        run.cost.read(n.id for n in candidates)
        current = [n for n in candidates if n.node_class in run.step_classes[index]]
        if not current:
            run.absence = Absence(
                index,
                "edge-lands-elsewhere",
                f"edges were followed and nothing they landed on is a `{step.node_class}`",
                reached,
            )
            return run
        if step.predicates:
            before = len(current)
            current = [n for n in current if satisfies(n, step.predicates)]
            if not current:
                run.absence = Absence(
                    index,
                    "predicate-unsatisfied",
                    f"nothing reached satisfies `{','.join(p.text() for p in step.predicates)}`",
                    before,
                )
                return run

    # By id, not by identity: `MirrorNode` is a mutable dataclass and so unhashable, and a
    # node reached by two edges must be one result rather than two.
    unique = {n.id: n for n in current}
    run.matched = [unique[i] for i in sorted(unique)]
    if not run.matched:
        run.absence = Absence(run.at, "no-match", "the path matched nothing", len(mirror.nodes))
    return run


# --- projection -------------------------------------------------------------------------------
def project(node: MirrorNode, select: list[str]) -> dict[str, Any]:
    """One matched node, rendered to the requested fields — plus its ``origin``.

    ``origin`` is null for a node from this corpus and names the package a node came from when
    a query spans. It is present whether or not the query spanned, so a client never has to
    distinguish "local" from "a server that does not attribute".
    """
    row: dict[str, Any] = {"origin": None}
    for name in select:
        if name == "node":
            row["node"] = node.id
        elif name == "class":
            row["class"] = node.node_class
        elif name == "label":
            row["label"] = node.label
        elif name == "description":
            row["description"] = node.description
        elif name == "body":
            row["body"] = node_text(node)
        elif name.startswith("properties."):
            row[name] = _property_of(node, name.split(".", 1)[1])
    return row


def parse_select(raw: str | None) -> tuple[list[str], Rejection | None]:
    """Split and validate a ``select``, rejecting a field nothing can project."""
    fields = [f.strip() for f in (raw or DEFAULT_SELECT).split(",") if f.strip()]
    if not fields:
        return list(DEFAULT_SELECT.split(",")), None
    for name in fields:
        if name in SELECTABLE or name.startswith("properties."):
            continue
        near = _near_miss(name, SELECTABLE)
        return (
            [],
            Rejection(
                0,
                "unknown-field",
                f"`{name}` is not projectable"
                + (f" — did you mean `{near}`?" if near else "")
                + f" (available: {', '.join(SELECTABLE)}, properties.<name>)",
            ),
        )
    return fields, None


# --- paths: how two nodes are related, as queries that run (contract 0.27.0) -------------------
# A port of upstream's `cmd/query/paths.rs`, not a reinvention of it: the bounds, the budget, the
# id forms, the grouping and the order are its, so a caller moving between the binary and this
# server reads the same answer. Every path returned has been run through `execute` above and its
# answer holds the target — a path this server spelled and did not run would be a guess about
# the grammar presented as a fact about the corpus.

#: Longest chain considered, in hops, when the caller names none.
PATHS_MAX_HOPS = 4
#: Runnable paths returned when the caller names no limit. Past it a path is counted, not run.
PATHS_LIMIT = 5
#: Node chains kept per class path, as evidence.
PATHS_EVIDENCE = 3
#: DFS steps before the search stops and says so (`complete: false`).
PATHS_BUDGET = 200_000


def _paths_resolve(mirror: Mirror, written: str) -> MirrorNode | None:
    """``reach/tailwater``, with or without ``.yml``, with or without the corpus directory."""
    want = written.strip().lstrip("/")
    want = want.removeprefix(".yidam/corpus/")
    want = want.removesuffix(".yml")
    return next((n for n in mirror.nodes if n.id == want), None)


def find_paths(
    mirror: Mirror,
    frm: str,
    to: str,
    *,
    max_hops: int = PATHS_MAX_HOPS,
    limit: int = PATHS_LIMIT,
) -> dict[str, Any]:
    """The typed paths between two nodes, each a query that runs and returns ``to``.

    Hops read edges in BOTH directions — a path is spelled ``<-rel-`` where it walks one
    backwards — because "how are these related" has no authoring direction, and a search that
    followed only outbound links would call two nodes unconnected when one merely cites the
    other. A node that does not resolve is a ``unknown-node`` rejection, never an empty list:
    the empty list asserts the two are unrelated, about a node this search never found.
    """
    max_hops = max(1, max_hops)
    limit = max(1, limit)

    def unknown(written: str, which: int) -> dict[str, Any]:
        return {
            "kind": "paths",
            "from": frm,
            "to": to,
            "scope": "local",
            "rejected": {
                "step": None,
                "code": "unknown-node",
                "message": f"`{written}` names no node in this corpus — write it as "
                f"`class/name`, the id `yidam query` prints (argument {which})",
            },
            "max_hops": max_hops,
            "paths": [],
            "found": 0,
            "returned": 0,
            "unchecked": 0,
            "withheld": [],
            "complete": True,
            "nearest": None,
        }

    source = _paths_resolve(mirror, frm)
    if source is None:
        return unknown(frm, 1)
    target = _paths_resolve(mirror, to)
    if target is None:
        return unknown(to, 2)

    index = {n.id: i for i, n in enumerate(mirror.nodes)}
    count = len(mirror.nodes)
    # Both directions of every edge `execute` can walk, per node, in corpus order. Only links
    # that resolve to a mirror node count — a citation of a catalog FILE is not a hop.
    arcs: list[list[tuple[str, str, int]]] = [[] for _ in range(count)]
    for frm_id, to_id, rel in _edges(mirror):
        i, j = index.get(frm_id), index.get(to_id)
        if i is None or j is None or i == j:
            continue
        forward, backward = (rel, "out", j), (rel, "in", i)
        if forward not in arcs[i]:
            arcs[i].append(forward)
        if backward not in arcs[j]:
            arcs[j].append(backward)

    s, t = index[source.id], index[target.id]
    dist: list[int | None] = [None] * count
    dist[t] = 0
    queue = deque([t])
    while queue:
        at = queue.popleft()
        here = dist[at] or 0
        for _, _, nxt in arcs[at]:
            if dist[nxt] is None:
                dist[nxt] = here + 1
                queue.append(nxt)

    # Every simple chain within the bound, pruned on distance, stopped at a work budget.
    found: list[tuple[list[int], list[tuple[str, str, int]]]] = []
    on_chain = [False] * count
    nodes: list[int] = [s]
    taken: list[tuple[str, str, int]] = []
    steps = 0

    def go(at: int) -> bool:
        nonlocal steps
        steps += 1
        if steps > PATHS_BUDGET:
            return False
        if at == t:
            found.append((list(nodes), list(taken)))
            return True
        depth = len(taken)
        for arc in arcs[at]:
            d = dist[arc[2]]
            if on_chain[arc[2]] or d is None or depth + 1 + d > max_hops:
                continue
            on_chain[arc[2]] = True
            nodes.append(arc[2])
            taken.append(arc)
            finished = go(arc[2])
            taken.pop()
            nodes.pop()
            on_chain[arc[2]] = False
            if not finished:
                return False
        return True

    on_chain[s] = True
    try:
        complete = go(s)
    except RecursionError:
        # Only a caller-set `max_hops` in the hundreds gets here. The search stopped before
        # enumerating every chain, which is what `complete: false` says — not a crash.
        complete = False

    def ident(i: int) -> str:
        return f"{mirror.nodes[i].id}.yml"

    def spell(chain_nodes: list[int], chain_arcs: list[tuple[str, str, int]]) -> str:
        out = mirror.nodes[chain_nodes[0]].node_class
        for (rel, direction, _), node in zip(chain_arcs, chain_nodes[1:], strict=True):
            hop = f"-{rel}->" if direction == "out" else f"<-{rel}-"
            out += f" {hop} {mirror.nodes[node].node_class}"
        return out

    # Grouped by spelling — what a caller would run — fewest hops first, then by text.
    by_path: dict[tuple[int, str], list[list[str]]] = {}
    for chain_nodes, chain_arcs in found:
        key = (len(chain_arcs), spell(chain_nodes, chain_arcs))
        by_path.setdefault(key, []).append([ident(n) for n in chain_nodes])

    target_id = ident(t)
    paths: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    unchecked = 0
    for (hops, text), evidence in sorted(by_path.items()):
        if len(paths) == limit:
            unchecked += 1
            continue
        chains = len(evidence)
        run = execute(mirror, text)
        if run.rejected is not None:
            withheld.append(
                {
                    "query": text,
                    "chains": chains,
                    "code": run.rejected.code,
                    "reason": run.rejected.message,
                }
            )
        elif any(n.id == target.id for n in run.matched):
            paths.append(
                {
                    "query": text,
                    "hops": hops,
                    "chains": chains,
                    "evidence": sorted(evidence)[:PATHS_EVIDENCE],
                    "matched": len(run.matched),
                }
            )
        else:
            withheld.append(
                {
                    "query": text,
                    "chains": chains,
                    "code": None,
                    "reason": f"ran, and its answer does not contain `{target_id}` — a chain "
                    "realises this path, so this is a defect in `--paths`, not a fact about "
                    "the corpus",
                }
            )

    return {
        "kind": "paths",
        "from": ident(s),
        "to": target_id,
        "scope": "local",
        "rejected": None,
        "max_hops": max_hops,
        "paths": paths,
        "found": len(by_path),
        "returned": len(paths),
        "unchecked": unchecked,
        "withheld": withheld,
        "complete": complete,
        "nearest": dist[s],
    }
