"""Framework-neutral multi-file STAAD intake boundary.

An authenticated API adapter must supply project identity and enforce its own
request size, streaming, session, CSRF, and authorization controls. This module
accepts bounded bytes, never parses undocumented .grd contents.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .durable import LocalArchiveStore
from .preservation import ArchiveError, Limits
from .staad_grid_companion import Upload, _name
from .staad_grid_durable import StoredStaadBundle, ingest_staad_bundle


@dataclass(frozen=True)
class IntakeReceipt:
    bundle_id: str
    model_object_id: str
    grid_object_id: str | None
    grid_status: str
    grid_parsed: str = 'not-attempted'
    grid_mapped: str = 'not-attempted'


def ingest_staad_uploads(
    store: LocalArchiveStore, files: Sequence[Upload], *, project_ref: str,
    namespace: str, policy_id: str, limits: Limits,
    selected_grid_filename: str | None = None,
    max_total_bytes: int | None = None,
) -> IntakeReceipt:
    """Validate a complete multi-file request before writing any source objects.

    A request contains exactly one .std/.sbk and at most one .grd. A .grd with
    a different stem requires explicit selection. Additional files are rejected
    rather than silently dropped. All file bytes are already resident in memory.
    """
    if not files:
        raise ArchiveError('NO_UPLOAD_FILES')
    if max_total_bytes is None:
        max_total_bytes = limits.maxBytes * 2
    if type(max_total_bytes) is not int or max_total_bytes <= 0:
        raise ArchiveError('INVALID_TOTAL_UPLOAD_LIMIT')
    models: list[Upload] = []
    grids: list[Upload] = []
    total = 0
    for file in files:
        if not isinstance(file, Upload) or not isinstance(file.content, bytes):
            raise ArchiveError('INVALID_UPLOAD')
        _, ext = _name(file.filename)
        total += len(file.content)
        if len(file.content) > limits.maxBytes or total > max_total_bytes:
            raise ArchiveError('UPLOAD_SIZE_LIMIT')
        if ext in ('.std', '.sbk'):
            models.append(file)
        elif ext == '.grd':
            grids.append(file)
        else:
            raise ArchiveError('UNSUPPORTED_UPLOAD_FILE')
    if len(models) != 1:
        raise ArchiveError('EXPECTED_ONE_STAAD_MODEL')
    if len(grids) > 1:
        raise ArchiveError('EXPECTED_AT_MOST_ONE_GRID')
    if grids and selected_grid_filename is None and _name(grids[0].filename)[0] != _name(models[0].filename)[0]:
        raise ArchiveError('EXPLICIT_GRID_SELECTION_REQUIRED')
    result: StoredStaadBundle = ingest_staad_bundle(
        store, models[0], tuple(grids), project_ref=project_ref,
        namespace=namespace, policy_id=policy_id, limits=limits,
        selected_filename=selected_grid_filename,
    )
    return IntakeReceipt(result.bundle_id, result.model.object_id,
                         result.grid.object_id if result.grid else None,
                         result.grid_status)
