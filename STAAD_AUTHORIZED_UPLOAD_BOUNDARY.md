# STAAD authorized upload boundary — local implementation candidate

This incremental slice adds `staad_api_boundary.py`, a transport-independent authorization gate. It requires an authenticated principal and a server-controlled project-write authorizer before calling the existing bounded multi-file intake. It supports a `.std`/`.sbk` source and an optional `.grd` companion. All original bytes and their hashes are preserved by the existing storage module; `.grd` parsing and mapping remain `not-attempted`.

## Security and integration boundary

This is **not** a deployed HTTP endpoint, a Supabase policy, a session verifier, a CSRF defense, a streaming upload parser, an atomic multi-object transaction, or an orphan cleanup worker. The host API must authenticate the user, authorize the project using trusted server-side state, enforce request size while streaming, and supply the server-side storage instance. The callback is a dependency injection seam, not proof of production authorization.

## Validation

Run `PYTHONPATH=src python -m unittest discover -s tests -q`. Local result: 128 tests passed (including 5 new authorization boundary tests). No live production authentication or deployment tests were performed.

## Repository status

This is a local candidate only. No GitHub commit or merge was made. Importer repo writes require exact-diff approval and separate authorization per `LINKOTEQ_PLUGIN_MIGRATION_CONTRACT.md`.
