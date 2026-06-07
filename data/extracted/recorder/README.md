# Recorder deed extractions

Reviewed structured reads (`*.deed.yaml`) of the Allen County Recorder instruments
under [`data/documents/recorder/`](../../documents/recorder/README.md). One file per
deed, named by the Recorder instrument number.

## Conventions

Grantor/grantee, parcels, consideration, and dates are read from the deed image/text
and never inferred. Each file records `doc_id`, `source_path`, `pages_read`, and a
provenance block. The `…-amazon-deed` file is the port-authority conveyance.
