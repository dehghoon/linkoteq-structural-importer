"""Durable STAAD model and optional .grd ingestion; no grid decoding.

The association record is the commit point. Ingested objects may remain orphaned
if a later write fails; production deployments need orphan cleanup and retention.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
import uuid

from .durable import LocalArchiveStore, StoredSource
from .preservation import ArchiveError, Limits
from .staad_grid_companion import Upload, attach_grid, _name


@dataclass(frozen=True)
class StoredStaadBundle:
    bundle_id: str
    model: StoredSource
    grid: StoredSource | None
    association: str | None
    grid_status: str


def ingest_staad_bundle(store: LocalArchiveStore, model: Upload,
                        companions: tuple[Upload, ...], *, project_ref: str,
                        namespace: str, policy_id: str, limits: Limits,
                        selected_filename: str | None = None) -> StoredStaadBundle:
    """Validate companion association before persisting; commit manifest last.

    The caller supplies authenticated project_ref; this function is not an API,
    authorization service, or distributed transaction coordinator.
    """
    chosen = attach_grid(model, companions, project_ref=project_ref,
                         namespace=namespace, policy_id=policy_id,
                         limits=limits, selected_filename=selected_filename)
    _, ext = _name(model.filename)
    model_stored = store.ingest(BytesIO(model.content), filename=model.filename,
        extension=ext, project_ref=project_ref, namespace=namespace,
        policy_id=policy_id, limits=limits)
    grid_stored = None
    if chosen is not None:
        grid_stored = store.ingest(BytesIO(chosen.archive.retrieve()),
            filename=chosen.archive.originalFilename, extension='.grd',
            project_ref=project_ref, namespace=namespace,
            policy_id=policy_id, limits=limits)
    bundle_id = uuid.uuid4().hex
    bundle = StoredStaadBundle(bundle_id, model_stored, grid_stored,
        chosen.association if chosen is not None else None,
        'source-companion-unparsed' if chosen is not None else 'missing')
    payload = {
        'schemaVersion': '0.1.0', 'bundleId': bundle_id,
        'projectRef': project_ref, 'namespace': namespace,
        'modelObjectId': model_stored.object_id,
        'modelSourceHash': model_stored.source_hash,
        'gridObjectId': grid_stored.object_id if grid_stored else None,
        'gridSourceHash': grid_stored.source_hash if grid_stored else None,
        'association': bundle.association, 'gridStatus': bundle.grid_status,
        'gridParsed': 'not-attempted', 'gridMapped': 'not-attempted',
    }
    folder = store.root / 'staad-bundles'
    folder.mkdir(mode=0o700, exist_ok=True)
    store._write_atomic(folder / (bundle_id + '.json'),
                        json.dumps(payload, sort_keys=True).encode('utf-8'))
    return bundle


def read_staad_bundle(store: LocalArchiveStore, bundle_id: str, *,
                      project_ref: str) -> dict[str, object]:
    """Read association and verify both immutable source objects and hashes."""
    if len(bundle_id) != 32 or any(c not in '0123456789abcdef' for c in bundle_id):
        raise ArchiveError('INVALID_BUNDLE_ID')
    path = store.root / 'staad-bundles' / (bundle_id + '.json')
    if not path.is_file() or path.is_symlink():
        raise ArchiveError('BUNDLE_NOT_FOUND')
    try:
        record = json.loads(path.read_text('utf-8'))
        if record['projectRef'] != project_ref or record['bundleId'] != bundle_id:
            raise ArchiveError('BUNDLE_NOT_FOUND')
        if record['gridStatus'] not in ('missing', 'source-companion-unparsed'):
            raise ArchiveError('BUNDLE_INTEGRITY_ERROR')
        model = store.retrieve(record['modelObjectId'], project_ref=project_ref)
        if sha256(model).hexdigest() != record['modelSourceHash']:
            raise ArchiveError('BUNDLE_INTEGRITY_ERROR')
        if record['gridObjectId'] is None:
            if record['gridSourceHash'] is not None or record['gridStatus'] != 'missing' or record['association'] is not None:
                raise ArchiveError('BUNDLE_INTEGRITY_ERROR')
        else:
            grid = store.retrieve(record['gridObjectId'], project_ref=project_ref)
            if sha256(grid).hexdigest() != record['gridSourceHash'] or record['gridStatus'] != 'source-companion-unparsed' or record['association'] not in ('filename-match','explicit-selection'):
                raise ArchiveError('BUNDLE_INTEGRITY_ERROR')
        return record
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ArchiveError('BUNDLE_INTEGRITY_ERROR') from exc
