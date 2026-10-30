"""Preservation-only, framework-neutral CSI upload boundary.

This module does not parse ETABS/SAP2000 tables, detect content, or map Core.
The authenticated host must supply a trusted principal, project authorization,
CSRF/session protection, quotas, and bounded streaming before calling it.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePath
from typing import Callable

from .durable import LocalArchiveStore, StoredSource
from .preservation import ArchiveError, Limits
from .staad_api_boundary import AuthenticatedPrincipal


@dataclass(frozen=True)
class CsiUploadRequest:
    project_ref: str
    namespace: str
    policy_id: str
    filename: str
    content: bytes


@dataclass(frozen=True)
class CsiPreservationReceipt:
    object_id: str
    source_hash: str
    byte_length: int
    declared_extension: str
    preserved: str = 'succeeded'
    parsed: str = 'not-attempted'
    mapped: str = 'not-attempted'
    grid_parsed: str = 'not-attempted'


def preserve_authorized_csi_upload(
    store: LocalArchiveStore,
    principal: AuthenticatedPrincipal,
    request: CsiUploadRequest,
    *,
    authorize_project_write: Callable[[AuthenticatedPrincipal, str], bool],
    limits: Limits,
) -> CsiPreservationReceipt:
    """Archive an approved CSI text export byte-exactly without interpretation."""
    if not isinstance(principal, AuthenticatedPrincipal) or not principal.subject_id.strip():
        raise ArchiveError('UNAUTHENTICATED')
    if not isinstance(request, CsiUploadRequest):
        raise ArchiveError('INVALID_UPLOAD_REQUEST')
    if not all(isinstance(x, str) and x.strip() for x in
               (request.project_ref, request.namespace, request.policy_id, request.filename)):
        raise ArchiveError('INVALID_UPLOAD_REQUEST')
    if not callable(authorize_project_write):
        raise ArchiveError('AUTHORIZER_REQUIRED')
    if not authorize_project_write(principal, request.project_ref):
        raise ArchiveError('PROJECT_ACCESS_DENIED')
    if not isinstance(request.content, bytes):
        raise ArchiveError('INVALID_UPLOAD')
    if len(request.content) > limits.maxBytes:
        raise ArchiveError('UPLOAD_SIZE_LIMIT')
    if '/' in request.filename or '\\' in request.filename or request.filename in ('.', '..'):
        raise ArchiveError('UNSAFE_FILENAME')
    extension = PurePath(request.filename).suffix
    if extension.casefold() not in ('.e2k', '.$et', '.s2k', '.$2k'):
        raise ArchiveError('UNSUPPORTED_CSI_EXTENSION')
    stored: StoredSource = store.ingest(
        BytesIO(request.content), filename=request.filename,
        extension=extension, project_ref=request.project_ref,
        namespace=request.namespace, policy_id=request.policy_id, limits=limits,
    )
    return CsiPreservationReceipt(stored.object_id, stored.source_hash,
                                  stored.byte_length, stored.declared_extension)
