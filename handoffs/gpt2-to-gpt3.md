# GPT-2 to GPT-3 — Proposed integration contract (NOT PUBLISHED)

Status: Local review candidate only. No importer repository commit or production deployment is claimed.

## Baseline
- Structural Core: `CORE_CONTRACT.md` on `main` declares v0.5; this is not evidence of a released tag.
- Importer: `main` currently documents specifications; this local prototype is not merged.
- Python runtime: stdlib-only implementation of preservation boundary; existing prototype uses POSIX `fcntl` and filesystem storage, not production object storage.

## Integration surface
- `accept_authorized_staad_upload(...)`: accepts one `.std` or `.sbk` plus optional `.grd`; preserves both without parsing grid content.
- `preserve_authorized_csi_upload(...)`: accepts one `.e2k`, `.$et`, `.s2k`, or `.$2k` as raw bytes, returning an immutable archive reference and explicit `not-attempted` statuses.
- Host application MUST authenticate the principal, validate project access against trusted server-side state, enforce quota atomically, bound uploads, implement CSRF/session controls, and configure retention and storage authorization.
- Starter: 5 imports per calendar/billing month **pending product clarification**; Pro and Company unlimited entitlement, but resource/security limits remain.
- Do not count a failed/unauthorized intake as a completed import without a separately approved quota lifecycle policy.

## Engineering capability boundary
- This candidate does not parse CSI grids or geometry, interpret `.grd`, map Structural Core, export IFC, analyze with PyNite, or establish engineering equivalence.
- Format extensions are admission hints only, not validated source-format detection.
- Source archive is independent of parsing success. Preserve unsupported source records.

## Local verification
- `PYTHONPATH=src python -m unittest discover -s tests -q`
- 135 tests passed in local container, including 7 new CSI preservation-boundary tests.
- No CI, deployment, production auth, billing, or Supabase tests were run.

## Required next gates
1. GPT-1 approves executable vendor semantics and sample oracles.
2. GPT-2 adds validated source detection, parsing, Core mapping and fidelity report increments.
3. GPT-3 supplies streaming upload adapter, trusted authorization and quota lifecycle, and durable multi-tenant storage.
4. GPT-5 reviews upload/auth/tenant isolation and retention.
5. GPT-4 verifies releases, CI, production and rollback.
