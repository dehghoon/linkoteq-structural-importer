"""Transport-independent authorized STAAD upload boundary.

The host API authenticates the principal, checks CSRF/session and streams with
limits BEFORE invoking this boundary. This boundary rechecks authorization and
request sizes and never trusts a client-supplied project identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .durable import LocalArchiveStore
from .preservation import ArchiveError, Limits
from .staad_grid_companion import Upload
from .staad_upload_intake import IntakeReceipt, ingest_staad_uploads


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    subject_id: str


@dataclass(frozen=True)
class StaadUploadRequest:
    project_ref: str
    namespace: str
    policy_id: str
    files: tuple[Upload, ...]
    selected_grid_filename: str | None = None


ProjectAuthorizer = Callable[[AuthenticatedPrincipal, str], bool]


def accept_authorized_staad_upload(
    store: LocalArchiveStore,
    principal: AuthenticatedPrincipal,
    request: StaadUploadRequest,
    *,
    authorize_project_write: ProjectAuthorizer,
    limits: Limits,
    max_total_bytes: int,
) -> IntakeReceipt:
    """Validate identity, project access and bounded files before persistence.

    The authorizer must query a trusted server-side authorization source.
    This function does not implement HTTP, CSRF, streaming or transactions.
    """
    if not isinstance(principal, AuthenticatedPrincipal) or not principal.subject_id.strip():
        raise ArchiveError('UNAUTHENTICATED')
    if not isinstance(request, StaadUploadRequest) or not request.project_ref.strip():
        raise ArchiveError('INVALID_UPLOAD_REQUEST')
    if not callable(authorize_project_write):
        raise ArchiveError('AUTHORIZER_REQUIRED')
    if not authorize_project_write(principal, request.project_ref):
        raise ArchiveError('PROJECT_ACCESS_DENIED')
    if not isinstance(request.files, tuple):
        raise ArchiveError('INVALID_UPLOAD_REQUEST')
    return ingest_staad_uploads(
        store, request.files, project_ref=request.project_ref,
        namespace=request.namespace, policy_id=request.policy_id,
        limits=limits, selected_grid_filename=request.selected_grid_filename,
        max_total_bytes=max_total_bytes,
    )
