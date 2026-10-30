# STAAD.Pro grid companion — durable local integration candidate

This increment adds `staad_grid_durable.py` and its tests. It uses the existing
`LocalArchiveStore` to persist a STAAD `.std`/`.sbk` model and an optional `.grd`
companion as separate immutable source objects. The final association JSON
contains object IDs, exact SHA-256 hashes, project scope, matching method, and
explicit `gridParsed=not-attempted`, `gridMapped=not-attempted` stages.

**Commit boundary:** The bundle association manifest is written last. If model
or companion persistence fails, no bundle is published. Previously persisted
objects can remain orphaned and require a retention/cleanup policy; this is
not a cross-object atomic transaction.

**Limitations:** This is a local Python reference implementation, not a web
upload endpoint, production authorization layer, or `.grd` decoder. A real
`.grd` fixture is needed before semantic parsing or grid visualization.

Reference: https://docs.bentley.com/LiveContent/web/STAAD.Pro-v2026.0.0/Help/en/topics/Modeling_Mode/t-stpst_Import_STAAD_Grid_File.html

Run: `PYTHONPATH=src python -m unittest discover -s tests -q`
