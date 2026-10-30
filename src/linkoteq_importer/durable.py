"""Local durable preservation infrastructure; no vendor parsing or Core mapping.

A single-process prototype: filesystem permissions, multi-process transactions,
retention and production authorization must be supplied by an integrating service.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO, Callable
import json
import contextlib
import fcntl
import os
import tempfile
import time
import uuid

from .preservation import ArchiveError, Limits, PhysicalSpan


@dataclass(frozen=True)
class StoredSource:
    object_id: str
    source_hash: str
    byte_length: int
    project_ref: str
    namespace: str
    policy_id: str
    original_filename: str
    declared_extension: str


class LocalArchiveStore:
    """Filesystem reference implementation, not a multi-tenant production service."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _write_atomic(path: Path, content: bytes) -> None:
        fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as output:
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            os.replace(name, path)
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def ingest(self, source: BinaryIO, *, filename: str, extension: str,
               project_ref: str, namespace: str, policy_id: str,
               limits: Limits, cancelled: Callable[[], bool] | None = None) -> StoredSource:
        if not all(isinstance(s, str) and s for s in (filename, project_ref, namespace, policy_id)):
            raise ArchiveError('INVALID_SOURCE_METADATA')
        object_id = uuid.uuid4().hex
        folder = self.root / object_id
        folder.mkdir(mode=0o700)
        started = time.monotonic()
        length = 0
        digest = sha256()
        try:
            with (folder / 'source.part').open('xb') as output:
                while True:
                    if cancelled and cancelled():
                        raise ArchiveError('CANCELLED')
                    if (time.monotonic() - started) * 1000 > limits.maxWallMillis:
                        raise ArchiveError('MAX_WALL_MILLIS_EXCEEDED')
                    chunk = source.read(min(65536, limits.maxBytes - length + 1))
                    if not isinstance(chunk, bytes):
                        raise ArchiveError('SOURCE_READ_INVALID')
                    if not chunk:
                        break
                    length += len(chunk)
                    if length > limits.maxBytes:
                        raise ArchiveError('MAX_BYTES_EXCEEDED')
                    digest.update(chunk)
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            metadata = StoredSource(object_id, digest.hexdigest(), length, project_ref,
                                    namespace, policy_id, filename, extension)
            # Manifest is committed only after source bytes are fully flushed.
            os.replace(folder / 'source.part', folder / 'source.bin')
            self._write_atomic(folder / 'manifest.json', json.dumps(vars(metadata),
                               ensure_ascii=False, sort_keys=True).encode('utf-8'))
            return metadata
        except BaseException:
            for path in folder.iterdir():
                path.unlink()
            folder.rmdir()
            raise

    def _folder(self, object_id: str) -> Path:
        if len(object_id) != 32 or any(c not in '0123456789abcdef' for c in object_id):
            raise ArchiveError('INVALID_OBJECT_ID')
        folder = self.root / object_id
        if not folder.is_dir() or folder.is_symlink():
            raise ArchiveError('ARCHIVE_NOT_FOUND')
        return folder

    def retrieve(self, object_id: str, *, project_ref: str) -> bytes:
        folder = self._folder(object_id)
        meta = json.loads((folder / 'manifest.json').read_text('utf-8'))
        if meta['project_ref'] != project_ref:
            raise ArchiveError('ARCHIVE_NOT_FOUND')
        source_path = folder / 'source.bin'
        if source_path.is_symlink():
            raise ArchiveError('HASH_MISMATCH')
        data = source_path.read_bytes()
        if len(data) != meta['byte_length'] or sha256(data).hexdigest() != meta['source_hash']:
            raise ArchiveError('HASH_MISMATCH')
        return data

    @contextlib.contextmanager
    def _ledger_lock(self, folder: Path):
        """POSIX advisory lock; all writers must cooperate."""
        lock_path = folder / '.ledger.lock'
        if lock_path.is_symlink():
            raise ArchiveError('UNSAFE_LEDGER_LOCK')
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(fd, 'rb') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        except BaseException:
            raise

    def commit_ledger(self, object_id: str, *, project_ref: str,
                      spans: tuple[PhysicalSpan, ...], limits: Limits) -> int:
        folder = self._folder(object_id)
        raw = self.retrieve(object_id, project_ref=project_ref)
        if len(spans) > limits.maxPhysicalSpans:
            raise ArchiveError('MAX_PHYSICAL_SPANS_EXCEEDED')
        cursor = 0
        for i, span in enumerate(spans):
            if (type(span.ordinal) is not int or type(span.startByte) is not int or
                    type(span.endByte) is not int or span.ordinal != i or span.startByte != cursor or
                span.endByte <= cursor or span.endByte > len(raw) or
                not isinstance(span.kind, str) or not span.kind or
                (span.decodedLine is not None and
                 (type(span.decodedLine) is not int or span.decodedLine < 1))):
                raise ArchiveError('INVALID_SPAN_COVERAGE')
            cursor = span.endByte
        if cursor != len(raw):
            raise ArchiveError('INVALID_SPAN_COVERAGE')
        with self._ledger_lock(folder):
            existing = []
            for path in folder.glob('ledger-*.json'):
                suffix = path.stem.removeprefix('ledger-')
                if suffix.isdecimal():
                    existing.append(int(suffix))
            revision = max(existing, default=-1) + 1
            payload = {'revision': revision, 'sourceHash': sha256(raw).hexdigest(),
                       'spans': [vars(s) for s in spans]}
            target = folder / f'ledger-{revision}.json'
            if target.exists() or target.is_symlink():
                raise ArchiveError('LEDGER_REVISION_CONFLICT')
            self._write_atomic(target,
                               json.dumps(payload, sort_keys=True).encode('utf-8'))
            return revision

    def read_ledger(self, object_id: str, *, project_ref: str, revision: int) -> dict:
        """Verify a committed ledger revision against immutable source content."""
        if type(revision) is not int or revision < 0:
            raise ArchiveError('INVALID_LEDGER_REVISION')
        folder = self._folder(object_id)
        raw = self.retrieve(object_id, project_ref=project_ref)
        path = folder / f'ledger-{revision}.json'
        if not path.is_file() or path.is_symlink():
            raise ArchiveError('LEDGER_NOT_FOUND')
        payload = json.loads(path.read_text('utf-8'))
        if type(payload.get('revision')) is not int or payload.get('revision') != revision or payload.get('sourceHash') != sha256(raw).hexdigest():
            raise ArchiveError('LEDGER_INTEGRITY_ERROR')
        try:
            spans = tuple(PhysicalSpan(**item) for item in payload['spans'])
        except (TypeError, KeyError, ValueError) as exc:
            raise ArchiveError('LEDGER_INTEGRITY_ERROR') from exc
        cursor = 0
        for i, span in enumerate(spans):
            if (type(span.ordinal) is not int or type(span.startByte) is not int or
                    type(span.endByte) is not int or span.ordinal != i or span.startByte != cursor or
                    span.endByte <= cursor or span.endByte > len(raw) or
                    (span.decodedLine is not None and span.decodedLine < 1)):
                raise ArchiveError('INVALID_SPAN_COVERAGE')
            cursor = span.endByte
        if cursor != len(raw):
            raise ArchiveError('INVALID_SPAN_COVERAGE')
        return payload
