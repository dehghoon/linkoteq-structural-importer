# SAP2000 GPT-3 Python upload service

Branch: `feature/gpt3-sap2000-upload-api`. This adapter consumes the verified
GPT-2 `build_gpt3_package` and `package_to_json`; it does not implement parsing.

## Run (development)

```sh
pip install -r requirements-gpt3-api.txt
PYTHONPATH=src SAP2000_IMPORTER_API_TOKEN='<private-random-token>' uvicorn linkoteq_importer.gpt3_upload_api:app --host 0.0.0.0 --port 8000
```

Next.js 3D Model uses `SAP2000_IMPORTER_API_URL` (Python service origin)
and `SAP2000_IMPORTER_API_TOKEN` (matching server-side token).
Do not expose either token to client JavaScript. No production deployment is
authorized by this branch.

POST `/api/import/sap2000` multipart fields: `file`, `project_id`.
Authorization: Bearer token. File extensions: `.s2k` and `.$2k`.
Maximum size: 20 MB. Returns full GPT-2 source-preserving JSON handoff.

The handoff is source-only and **not a validated Core StructuralModel**.
It retains raw archive bytes and diagnostic/fidelity information. UI must
never present it as analysis-ready or silently convert source units.
A separate production review is required for durable archive storage,
authorization by project, rate limiting, and retention policy.
