# STAAD multi-file intake — implementation candidate

This increment introduces `staad_upload_intake.py`, a framework-neutral bounded multi-file request coordinator for one `.std`/`.sbk` model plus an optional `.grd` companion. It validates all supplied files before persisting any source objects and uses the existing durable bundle implementation. It rejects unexpected files, multiple models, multiple grids, and mismatched filenames unless the grid was explicitly selected. The response contains bundle/object IDs and an honest `not-attempted` grid parsing/mapping status.

**Boundary:** This is NOT a production HTTP upload route, a streaming parser, a `.grd` decoder, a cloud storage transaction, or a deployment. API authorization, streaming limits, storage rollback/orphan cleanup, and a real `.grd` fixture remain separate integration requirements. Original bytes are preserved without interpreting grid semantics.

**Test:** `PYTHONPATH=src python -m unittest discover -s tests -q`.

**Source:** Bentley STAAD.Pro documentation confirms custom grids are saved to companion `.grd` files. https://docs.bentley.com/LiveContent/web/STAAD.Pro-v2026.0.0/Help/en/topics/Modeling_Mode/t-stpst_Import_STAAD_Grid_File.html
