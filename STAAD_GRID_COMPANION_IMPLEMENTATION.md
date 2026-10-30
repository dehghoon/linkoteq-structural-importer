# STAAD.Pro .grd companion intake — local implementation candidate

Bentley documentation confirms custom modeling grids are saved in a separate `.grd` file adjacent to the STAAD input model. `.sbk` is a backup copy of `.std`, not the companion grid.

Reference: https://docs.bentley.com/LiveContent/web/STAAD.Pro-v2026.0.0/Help/en/topics/Modeling_Mode/t-stpst_Import_STAAD_Grid_File.html

## Scope

- `attach_grid()` accepts a `.std` or `.sbk` upload and optional `.grd` companions.
- Automatic association only for matching case-insensitive basenames; explicit exact filename selection supports a different basename.
- Exact original `.grd` bytes and SHA-256 are preserved in the existing bounded `Archive` representation; no decoding or inferred grid claims.
- Unsafe names, duplicate/ambiguous companions, invalid extensions and oversized model/companion files are rejected.
- Fidelity stages are `preserved=succeeded`; parsing, semantic understanding, mapping, visualization, IFC export and analysis are `not-attempted`.

## Limitations and next integration gate

This is an **in-memory** library candidate, not a production upload API. The caller must durably and transactionally persist **both** source archives before acknowledging upload. No real `.grd` sample has been supplied, so no `.grd` parser or grid-coordinate extraction is claimed. Do not promote to Core or IFC without an approved schema and sample-backed parser tests. The `.grd` may be absent, and missing is not evidence of missing geometric grid in the original application.

## Run tests

`PYTHONPATH=src python -m unittest discover -s tests -q`
