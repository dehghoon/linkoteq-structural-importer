"""Optional FastAPI adapter for the verified GPT-2 SAP2000 handoff.

Deploy this as a separate Python service; do not embed the parser in Next.js.
Requires: pip install fastapi uvicorn python-multipart
Start: uvicorn linkoteq_importer.gpt3_upload_api:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
import secrets
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response

from linkoteq_importer.sap2000_gpt3_package import (
    DEFAULT_LIMITS, build_gpt3_package, package_to_json,
)

app = FastAPI(title="Linkoteq SAP2000 Import Adapter", docs_url=None, redoc_url=None)

@app.post("/api/import/sap2000")
async def import_sap2000(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    authorization: str | None = Header(default=None),
) -> Response:
    token = os.environ.get("SAP2000_IMPORTER_API_TOKEN")
    if not token or not secrets.compare_digest(authorization or "", "Bearer " + token):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    filename = file.filename or ""
    if not filename.lower().endswith((".s2k", ".$2k")):
        raise HTTPException(status_code=400, detail="UNSUPPORTED_SAP_EXTENSION")
    if not project_id or len(project_id) > 128:
        raise HTTPException(status_code=400, detail="INVALID_PROJECT_ID")
    data = await file.read(DEFAULT_LIMITS.max_bytes + 1)
    if len(data) > DEFAULT_LIMITS.max_bytes:
        raise HTTPException(status_code=413, detail="SAP2000_FILE_TOO_LARGE")
    try:
        payload = build_gpt3_package(data, filename=filename, project_id=project_id)
        return Response(content=package_to_json(payload, indent=None), media_type="application/json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
