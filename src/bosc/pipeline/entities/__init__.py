"""Entity resolution — a small cross-document graph of who relates to whom.

Phase C item 5. Parties appear across deeds, NPDES permits, and SoS business
filings under inconsistent spellings ("BISTROZZI LLC" vs "Bistrozzi LLC, a
Delaware Limited Liability Company"). This module normalizes them to a canonical
key, merges the variants into one :class:`Entity`, classifies each (government /
corporate / individual / trust / facility / water), and records the relationships
between them (conveyances, utility operation, discharge, plus — from SoS filings —
who organized an LLC and its registered agent). A registered agent shared by more
than one entity is flagged with a ``shared_agent`` signal.

Classification follows the *conservative* posture of Periplus's owner-
classification rationale (see ``docs/reference/periplus/`` / the ``../gis`` fork):
prefer a plain corporate/individual label over a "shell" accusation; record
shell-adjacent signals (e.g. a Delaware registration) as evidence, not verdicts.
"""

from __future__ import annotations

from bosc.pipeline.entities._enrich import (
    enrich_with_federal_awards as enrich_with_federal_awards,
)
from bosc.pipeline.entities._enrich import (
    enrich_with_lei as enrich_with_lei,
)
from bosc.pipeline.entities._enrich import (
    enrich_with_parcel_owners as enrich_with_parcel_owners,
)
from bosc.pipeline.entities._enrich import (
    enrich_with_places as enrich_with_places,
)
from bosc.pipeline.entities._enrich import (
    enrich_with_relation_classes as enrich_with_relation_classes,
)
from bosc.pipeline.entities._enrich import (
    enrich_with_rsei_ownership as enrich_with_rsei_ownership,
)
from bosc.pipeline.entities._graph import (
    Entity as Entity,
)
from bosc.pipeline.entities._graph import (
    EntityGraph as EntityGraph,
)
from bosc.pipeline.entities._graph import (
    Relationship as Relationship,
)
from bosc.pipeline.entities._graph import (
    build_entity_graph as build_entity_graph,
)
from bosc.pipeline.entities._names import (
    RELATION_CLASS_ORDER as RELATION_CLASS_ORDER,
)
from bosc.pipeline.entities._names import (
    RelationClass as RelationClass,
)
from bosc.pipeline.entities._names import (
    _base_permit as _base_permit,
)
from bosc.pipeline.entities._names import (
    _looks_like_person as _looks_like_person,
)
from bosc.pipeline.entities._names import (
    _parse_trustee_recital as _parse_trustee_recital,
)
from bosc.pipeline.entities._names import (
    _split_multi as _split_multi,
)
from bosc.pipeline.entities._names import (
    _split_principal as _split_principal,
)
from bosc.pipeline.entities._names import (
    classify as classify,
)
from bosc.pipeline.entities._names import (
    normalize_name as normalize_name,
)
