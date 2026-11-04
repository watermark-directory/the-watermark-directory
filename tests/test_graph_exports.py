"""Graph exports — RDF (Turtle + JSON-LD) + GraphML over the corpus mirror (#1574, epic #1560 D1).

These serializers are the Python peer of yidam's ``export_rdf.rs`` / ``export_graphml.rs``: same
subject names (``urn:yidam:<corpus>/node/<class>/<name>``), same vocabulary (owl/rdfs/skos/prov + ``yidam:``),
same relationship→camelCase sanitizer, same link-target resolution, same GraphML key set.

Most tests here assert that shape against hand-written expectations. That is necessary and was
not sufficient: it pins what BOSC *meant* to emit, never what yidam actually emits, so the two
can agree with their own fixtures and disagree with each other. They did — the binary emitted
`yidam:genesisDate` over this corpus and BOSC did not, for as long as the claim above went
unchecked (#2053).

The conformance tests at the bottom close that: they run the **real pinned binary** over the
same mirror and compare structurally. They skip when it is absent; CI installs it, so the
claim in this docstring is now enforced rather than asserted.

At the ``cli/v0.23.0`` re-pin the binary renamed every RDF subject
(``yidam://corpus/<id>`` → ``urn:yidam:<genesis[:12]>/node/<id>``) and moved the ``yidam:``
namespace — and the namespace move was invisible here, because the vocabulary was compared by
its ``yidam:`` *prefix*, never by what the prefix expands to. The prefix declarations are
compared now too.
"""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from watermark.config import Settings
from watermark.hypotheses import HYPOTHESES, HypothesisAssessment
from watermark.site import yidam_cli
from watermark.site.corpus_mirror import (
    Mirror,
    MirrorLink,
    MirrorNode,
    build_mirror,
    project_mirror,
    write_mirror,
)
from watermark.site.feeds import ConceptItem, EntityNode, LeadItem, PersonItem, RelationshipEdge
from watermark.site.graph_exports import (
    ExportProvenance,
    NoCorpusIdentityError,
    _git_genesis_date,
    _git_genesis_hash,
    property_local_name,
    render_exports,
    render_graphml,
    render_jsonld,
    render_turtle,
    resolve_link_target,
    resolve_provenance,
    subject_iri,
    write_exports,
)

GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"

PROV = ExportProvenance(
    domain="BOSC corpus mirror — Lima, Ohio",
    commit="abc1234",
    genesis="2026-01-01",
    generated_at="2026-01-01T00:00:00+00:00",
    genesis_hash="0123456789abcdef0123456789abcdef01234567",
)
# What every subject in PROV's exports hangs off — the genesis hash, twelve characters.
CORPUS_IRI = "urn:yidam:0123456789ab"


# --- a small, connected synthetic mirror (the corpus_mirror projection over toy feeds) -------
def _mirror() -> Mirror:
    entities = [
        EntityNode(key="GOOGLE", display="Google LLC", kind="corporate", classification="operator"),
        EntityNode(
            key="npdes:1AB00001", display="NPDES 1AB00001", kind="permit", classification="permit"
        ),
    ]
    relationships = [
        RelationshipEdge(src="GOOGLE", rel="operates", dst="npdes:1AB00001", source="permit.yaml"),
    ]
    concepts = [
        ConceptItem(slug="7q10", title="7Q10", summary='A design low flow, with "quotes".'),
    ]
    people = [PersonItem(slug="jane-doe", name="Jane Doe", entity_key="GOOGLE", expanded=True)]
    leads = [
        LeadItem(
            id="lead-1",
            kind="question",
            status="unanswered",
            tag="open",
            title="An open question",
            detail="Still chasing.",
            source="audit.md",
        )
    ]
    open_claims = [
        HypothesisAssessment(site="lima", hypothesis="water", signal="watch", tag="open"),
    ]
    return project_mirror(
        site="lima",
        site_label="Lima, Ohio",
        entities=entities,
        relationships=relationships,
        concepts=concepts,
        people=people,
        leads=leads,
        hypotheses=HYPOTHESES,
        open_claims=open_claims,
    )


# --- link-target resolution (yidam model::resolve_link_target) ------------------------------
def test_resolve_link_target_matches_yidam() -> None:
    assert resolve_link_target("reach", "alpha.yml") == "reach/alpha"
    assert resolve_link_target("reach", "../concept/formation.yml") == "concept/formation"
    assert resolve_link_target("reach", "./beta.yml") == "reach/beta"
    # escapes the corpus dir → returned verbatim
    assert resolve_link_target("reach", "../../skills/x.md") == "../../skills/x.md"


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_property_local_name_sanitizes() -> None:
    assert property_local_name("causes") == "causes"
    assert property_local_name("relates to") == "relatesTo"
    assert property_local_name("assessed-under") == "assessedUnder"
    assert property_local_name("link") == "linksTo"
    assert property_local_name("???") == "linksTo"


# --- RDF: Turtle ----------------------------------------------------------------------------
def test_turtle_has_prefixes_ontology_header_and_provenance() -> None:
    ttl = render_turtle(_mirror(), PROV)
    assert "@prefix yidam: <https://goedelsoup.github.io/yidam/ontology#> ." in ttl
    assert "a owl:Ontology" in ttl
    assert "BOSC corpus mirror — Lima, Ohio" in ttl
    assert 'yidam:commit "abc1234"' in ttl
    assert 'yidam:genesisDate "2026-01-01"' in ttl
    assert "^^xsd:dateTime" in ttl


def test_turtle_types_instances_and_carries_named_relationships() -> None:
    mirror = _mirror()
    ttl = render_turtle(mirror, PROV)
    # every instance is typed by its class and reachable by its full IRI
    for node in mirror.nodes:
        assert f"<{CORPUS_IRI}/node/{node.id}>" in ttl
    assert "a yidam:concept" in ttl
    assert "a yidam:relation" in ttl
    # a named relationship becomes a yidam: object property + subproperty declaration
    assert "yidam:linksTo a owl:ObjectProperty ." in ttl
    assert "rdfs:subPropertyOf yidam:linksTo" in ttl
    # the concept's quoted definition is escaped
    assert 'skos:definition "A design low flow, with \\"quotes\\"."' in ttl


def test_turtle_is_deterministic() -> None:
    mirror = _mirror()
    assert render_turtle(mirror, PROV) == render_turtle(mirror, PROV)


# --- RDF: JSON-LD ---------------------------------------------------------------------------
def test_jsonld_is_valid_with_context_and_graph() -> None:
    mirror = _mirror()
    doc = json.loads(render_jsonld(mirror, PROV))
    assert doc["@context"]["yidam"] == "https://goedelsoup.github.io/yidam/ontology#"
    graph = doc["@graph"]
    by_id = {o["@id"]: o for o in graph}

    ontology = by_id[CORPUS_IRI]
    assert ontology["@type"] == "owl:Ontology"
    assert ontology["prov:generatedAtTime"] == {
        "@value": "2026-01-01T00:00:00+00:00",
        "@type": "xsd:dateTime",
    }

    # the resolved entity relationship edge points from GOOGLE to the permit
    google = next(n for n in mirror.nodes if n.name and n.label == "Google LLC")
    google_obj = by_id[f"{CORPUS_IRI}/node/{google.id}"]
    assert google_obj["@type"] == "yidam:artifact"
    # every yidam:* relationship value dereferences to an @id
    for key, value in google_obj.items():
        if key.startswith("yidam:"):
            entries = value if isinstance(value, list) else [value]
            for entry in entries:
                assert entry["@id"].startswith(f"{CORPUS_IRI}/")


def test_jsonld_classes_and_properties_declared() -> None:
    doc = json.loads(render_jsonld(_mirror(), PROV))
    ids = {o["@id"] for o in doc["@graph"]}
    assert "yidam:concept" in ids
    assert "yidam:linksTo" in ids
    types = {o["@id"]: o["@type"] for o in doc["@graph"]}
    assert types["yidam:concept"] == "owl:Class"
    assert types["yidam:linksTo"] == "owl:ObjectProperty"


# --- GraphML --------------------------------------------------------------------------------
def test_graphml_round_trips_through_xml_parser() -> None:
    mirror = _mirror()
    xml = render_graphml(mirror, PROV)
    root = ET.fromstring(xml)
    graph = root.find(f"{GRAPHML_NS}graph")
    assert graph is not None
    nodes = graph.findall(f"{GRAPHML_NS}node")
    edges = graph.findall(f"{GRAPHML_NS}edge")
    # one node per mirror instance; edges = resolved (non-dangling) links
    assert len(nodes) == len(mirror.nodes)
    resolved_edges = render_exports(mirror, PROV)[0].edge_count
    assert len(edges) == resolved_edges

    node_ids = {n.get("id") for n in nodes}
    assert node_ids == {node.id for node in mirror.nodes}
    # every edge endpoint is a real node (no dangling edge emitted)
    for edge in edges:
        assert edge.get("source") in node_ids
        assert edge.get("target") in node_ids


def test_graphml_nodes_carry_attributes_and_escape() -> None:
    xml = render_graphml(_mirror(), PROV)
    assert '<data key="commit">abc1234</data>' in xml
    assert 'key="outgoing_links"' in xml
    assert 'key="incoming_links"' in xml
    # edge `type` carries the mirror's raw relationship (the relation node fans out from→to its
    # subject/object entities); GraphML keeps it verbatim (unlike the RDF camelCase property).
    assert 'key="type">from</data>' in xml
    assert 'key="type">to</data>' in xml


def test_graphml_description_truncates_to_200_chars() -> None:
    long = "x" * 400
    node = MirrorNode(
        "concept", "long", label="Long", description=long, links=[MirrorLink("long.yml", "self")]
    )
    xml = render_graphml(Mirror(site="lima", nodes=[node]), PROV)
    assert "x" * 200 in xml
    assert "x" * 201 not in xml


# --- unresolved link targets (belt-and-braces: the real mirror never dangles) ---------------
def test_unresolved_target_becomes_owl_thing_and_skips_graphml_edge() -> None:
    node = MirrorNode(
        "concept",
        "alpha",
        label="Alpha",
        links=[MirrorLink("missing.yml", "link")],  # resolves to concept/missing, not present
    )
    mirror = Mirror(site="lima", nodes=[node])

    ttl = render_turtle(mirror, PROV)
    assert f"<{CORPUS_IRI}/node/concept/missing> a owl:Thing" in ttl
    assert "unresolved link target" in ttl

    doc = json.loads(render_jsonld(mirror, PROV))
    thing = next(o for o in doc["@graph"] if o["@id"] == f"{CORPUS_IRI}/node/concept/missing")
    assert thing["@type"] == "owl:Thing"

    xml = render_graphml(mirror, PROV)
    root = ET.fromstring(xml)
    graph = root.find(f"{GRAPHML_NS}graph")
    assert graph is not None
    assert graph.findall(f"{GRAPHML_NS}edge") == []  # dangling edge skipped


# --- writing --------------------------------------------------------------------------------
def test_subject_iri_names_catalog_escapes_as_catalog_entries() -> None:
    """yidam's ``reference_for``: an escape into the catalog is a catalog reference, not a node."""
    assert subject_iri(CORPUS_IRI, "concept/alpha") == f"{CORPUS_IRI}/node/concept/alpha"
    assert subject_iri(CORPUS_IRI, "../../catalog/aedg.md") == f"{CORPUS_IRI}/catalog/aedg"
    assert subject_iri(CORPUS_IRI, "catalog/x.md") == f"{CORPUS_IRI}/catalog/x"
    # a node merely NAMED with `catalog/` in its path stays a node — the split needs a climb
    assert subject_iri(CORPUS_IRI, "record/catalog/x") == f"{CORPUS_IRI}/node/record/catalog/x"


def test_rdf_refuses_a_corpus_with_no_identity_and_graphml_does_not() -> None:
    """No genesis hash → no RDF, never a stand-in name; GraphML names no subjects, so it stays."""
    nameless = ExportProvenance(domain=PROV.domain, commit=PROV.commit)
    with pytest.raises(NoCorpusIdentityError):
        render_turtle(_mirror(), nameless)
    with pytest.raises(NoCorpusIdentityError):
        render_jsonld(_mirror(), nameless)
    assert [e.fmt for e in render_exports(_mirror(), nameless)] == ["graphml"]


def test_genesis_hash_is_withheld_from_a_shallow_or_nested_checkout(tmp_path: Path) -> None:
    """The two routes to a wrong identity yidam refuses, refused here the same way."""
    repo = _git_repo(tmp_path / "repo")
    genesis = _git(repo, "rev-parse", "HEAD")
    assert _git_genesis_hash(repo) == genesis
    # nested: git answers for the ENCLOSING repository, whose genesis names another corpus
    (repo / "inner").mkdir()
    assert _git_genesis_hash(repo / "inner") == ""
    assert _git_genesis_date(repo / "inner") == ""
    # shallow: the boundary commit looks exactly like a root from inside
    _commit(repo, "second")
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )
    assert _git(shallow, "rev-list", "--max-parents=0", "HEAD") != genesis  # the trap, live
    assert _git_genesis_hash(shallow) == ""
    assert _git_genesis_date(shallow) == ""


def test_write_exports_emits_three_named_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "exports"
    exports = write_exports(_mirror(), out, PROV)
    assert {e.filename for e in exports} == {"corpus.ttl", "corpus.jsonld", "corpus.graphml"}
    assert {e.name for e in exports} == {
        "corpus-graph.ttl",
        "corpus-graph.jsonld",
        "corpus-graph.graphml",
    }
    for exp in exports:
        assert (out / exp.filename).is_file()
        assert (out / exp.filename).read_text(encoding="utf-8") == exp.text
        assert exp.node_count == len(_mirror().nodes)
    # media types line up with the formats
    by_fmt = {e.fmt: e.media_type for e in exports}
    assert by_fmt == {
        "turtle": "text/turtle",
        "jsonld": "application/ld+json",
        "graphml": "application/graphml+xml",
    }


# --- conformance against the real yidam binary (#2053) ---------------------------------------
#
# The reason this exists: this module's docstring claims fidelity to yidam's `export_rdf.rs` /
# `export_graphml.rs`, and until now nothing checked it. Measured when the check was written,
# GraphML was structurally identical while RDF Turtle had already drifted — the binary emitted
# `yidam:genesisDate` and BOSC did not, because `resolve_provenance` never populated a field the
# renderer had always supported. Counts agreed; vocabulary did not. That is exactly the shape of
# the `open-questions` divergence that went unnoticed for months (#2051).
#
# Structural, never byte-wise. Turtle statement order and GraphML attribute order are
# serialization details neither side promises, and a byte diff would fail on them constantly —
# which teaches everyone to ignore the check, the one failure mode worse than not having it.
def _graphml_shape(path: Path) -> tuple[set[str], set[tuple[str, str]], set[str]]:
    """(node ids, directed edges, `attr.name` key set) — what both renderers must agree on."""
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    root = ET.parse(path).getroot()
    graph = root.find("g:graph", ns)
    assert graph is not None, f"{path} has no <graph>"
    return (
        {n.get("id") or "" for n in graph.findall("g:node", ns)},
        {(e.get("source") or "", e.get("target") or "") for e in graph.findall("g:edge", ns)},
        {k.get("attr.name") or "" for k in root.findall("g:key", ns)},
    )


def _turtle_shape(path: Path) -> tuple[set[str], set[str], dict[str, str]]:
    """(subject IRIs, `yidam:` predicate vocabulary, prefix → namespace) — the ontology surface.

    The prefix map is the third leg because the second compares *names under a prefix*: at the
    v0.23.0 re-pin the binary moved `yidam:` to another namespace and this shape, comparing only
    `yidam:commit` against `yidam:commit`, called the two exports identical. Only prefixes BOTH
    sides declare are compared — declaring an unused `rdf:` is serialization, not vocabulary.
    """
    text = path.read_text(encoding="utf-8")
    return (
        set(re.findall(r"<(urn:yidam:[^>]+)>", text)),
        set(re.findall(r"(?<![:\w])(yidam:[A-Za-z][A-Za-z0-9]*)\b", text)),
        dict(re.findall(r"^@prefix\s+(\w+):\s*<([^>]+)>", text, flags=re.MULTILINE)),
    )


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        message,
    )


def _git_repo(path: Path) -> Path:
    """A real, full-history repository at `path` — RDF names a corpus by its own genesis."""
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q")
    _commit(path, "genesis")
    return path


def _binary_can(fmt: str) -> bool:
    """Whether the pinned binary was built with the feature `fmt` needs."""
    if not yidam_cli.usable():
        return False
    binary = yidam_cli.yidam_path()
    assert binary is not None
    listed = subprocess.run(
        [str(binary), "export", "--list"], capture_output=True, text=True
    ).stdout
    return any(line.strip().startswith(fmt) and "✓" in line for line in listed.splitlines())


@pytest.mark.skipif(not _binary_can("graphml"), reason="no yidam binary that can export graphml")
def test_graphml_matches_the_real_yidam_renderer(tmp_path: Path) -> None:
    settings = Settings(site="lima", data_dir=REPO_ROOT / "data")
    mirror = build_mirror(settings)
    corpus = tmp_path / ".yidam" / "corpus"
    write_mirror(mirror, corpus)
    write_exports(mirror, tmp_path / "ours", resolve_provenance(settings))

    binary = yidam_cli.yidam_path()
    assert binary is not None
    out = tmp_path / "theirs.graphml"
    subprocess.run(
        [str(binary), "export", "--format", "graphml", "--out", str(out)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    ours = _graphml_shape(tmp_path / "ours" / "corpus.graphml")
    theirs = _graphml_shape(out)
    assert ours[0] == theirs[0], "node sets differ"
    assert ours[1] == theirs[1], "edge sets differ"
    assert ours[2] == theirs[2], "GraphML key schema differs"


@pytest.mark.skipif(not _binary_can("rdf"), reason="the yidam binary lacks --features export-graph")
def test_turtle_matches_the_real_yidam_renderer(tmp_path: Path) -> None:
    """The half that had already drifted. `yidam:genesisDate` is the one this caught.

    The corpus is committed into a repository of its own first: since v0.23.0 the binary names
    every subject by the corpus's genesis commit and refuses a directory that has none. Ours is
    handed the same genesis, so the two name the same corpus.
    """
    settings = Settings(site="lima", data_dir=REPO_ROOT / "data")
    mirror = build_mirror(settings)
    corpus = tmp_path / ".yidam" / "corpus"
    write_mirror(mirror, corpus)
    _git_repo(tmp_path)
    prov = resolve_provenance(settings)
    prov.genesis_hash = _git(tmp_path, "rev-parse", "HEAD")
    write_exports(mirror, tmp_path / "ours", prov)

    binary = yidam_cli.yidam_path()
    assert binary is not None
    out = tmp_path / "theirs.ttl"
    subprocess.run(
        [str(binary), "export", "--format", "rdf", "--rdf-format", "turtle", "--out", str(out)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    our_subjects, our_preds, our_ns = _turtle_shape(tmp_path / "ours" / "corpus.ttl")
    their_subjects, their_preds, their_ns = _turtle_shape(out)
    assert our_subjects, "no urn:yidam: subjects at all — the shape is reading the wrong scheme"
    assert our_subjects == their_subjects, (
        f"subject IRIs differ — only ours: {sorted(our_subjects - their_subjects)[:5]}, "
        f"only theirs: {sorted(their_subjects - our_subjects)[:5]}"
    )
    shared = our_ns.keys() & their_ns.keys()
    assert "yidam" in shared
    assert {k: our_ns[k] for k in shared} == {k: their_ns[k] for k in shared}, "namespaces differ"
    assert our_preds == their_preds, (
        f"the yidam: ontology vocabulary differs — "
        f"only ours: {sorted(our_preds - their_preds)}, only theirs: {sorted(their_preds - our_preds)}"
    )
