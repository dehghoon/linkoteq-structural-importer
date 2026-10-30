"""STAAD.Pro .grd companion intake. No undocumented grid decoding."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal
from .preservation import Archive, ArchiveError, Limits, archive_bytes, fidelity_report


@dataclass(frozen=True)
class Upload:
    filename: str
    content: bytes


@dataclass(frozen=True)
class GridCompanion:
    archive: Archive
    model_source_hash: str
    association: Literal["filename-match", "explicit-selection"]
    grid_origin: Literal["source-companion-unparsed"] = "source-companion-unparsed"
    parsing_status: Literal["not-attempted"] = "not-attempted"

    def report(self) -> dict[str, object]:
        result = fidelity_report(self.archive)
        result.update({"modelSourceHash": self.model_source_hash,
                       "association": self.association, "gridOrigin": self.grid_origin})
        return result


def _name(filename: str) -> tuple[str, str]:
    if not isinstance(filename, str) or not filename or "\\" in filename or "/" in filename or "\x00" in filename:
        raise ArchiveError("UNSAFE_UPLOAD_FILENAME")
    if filename in (".", "..") or filename.strip() != filename:
        raise ArchiveError("UNSAFE_UPLOAD_FILENAME")
    p = PurePosixPath(filename)
    if not p.stem or not p.suffix:
        raise ArchiveError("INVALID_UPLOAD_EXTENSION")
    return p.stem.casefold(), p.suffix.casefold()


def attach_grid(model: Upload, companions: tuple[Upload, ...], *,
                project_ref: str, namespace: str, policy_id: str,
                limits: Limits, selected_filename: str | None = None) -> GridCompanion | None:
    """Archive an unparsed .grd matching a STAAD model, or an explicitly selected .grd.

    Upload is an in-memory intake candidate. The caller must persist archives using
    the approved durable storage transaction before acknowledging ingestion.
    """
    stem, extension = _name(model.filename)
    if extension not in (".std", ".sbk"):
        raise ArchiveError("NOT_STAAD_MODEL")
    model_archive = archive_bytes(model.content, filename=model.filename,
        extension=extension, project_ref=project_ref, namespace=namespace,
        policy_id=policy_id, limits=limits)
    names: set[str] = set()
    for companion in companions:
        _, suffix = _name(companion.filename)
        if suffix != ".grd":
            raise ArchiveError("NON_GRID_COMPANION")
        if companion.filename in names:
            raise ArchiveError("DUPLICATE_COMPANION_FILENAME")
        names.add(companion.filename)
    if selected_filename is not None:
        matches = [c for c in companions if c.filename == selected_filename]
        if len(matches) != 1:
            raise ArchiveError("SELECTED_GRID_NOT_FOUND")
        chosen = matches[0]
        association = "explicit-selection"
    else:
        matches = [c for c in companions if _name(c.filename)[0] == stem]
        if len(matches) > 1:
            raise ArchiveError("AMBIGUOUS_GRID_COMPANION")
        if not matches:
            return None
        chosen = matches[0]
        association = "filename-match"
    grid_archive = archive_bytes(chosen.content, filename=chosen.filename,
        extension=".grd", project_ref=project_ref, namespace=namespace,
        policy_id=policy_id, limits=limits)
    return GridCompanion(grid_archive, model_archive.sourceHash, association)
