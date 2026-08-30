"""
Resource Knowledge Base Loader
==============================

Loads and validates resources.json and sources.json against domain schemas.

Design rules:
- All resource data must pass Pydantic validation before being used.
- Source references are validated: every resource.source_id must exist in sources.
- Duplicate IDs are detected and reported.
- No data is fabricated or transformed — the loader reflects what the file contains.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from app.schemas.domain import Resource, Source

logger = logging.getLogger("migrantaid")


class DataLoadError(Exception):
    """Raised when data files cannot be loaded or validated."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


class ResourceKB:
    """In-memory resource knowledge base loaded from JSON files."""

    def __init__(
        self,
        resources: list[Resource],
        sources: list[Source],
        dataset_version: str,
    ):
        self.resources = resources
        self.sources = sources
        self.dataset_version = dataset_version

        # Build lookup indices
        self._resources_by_id: dict[str, Resource] = {r.resource_id: r for r in resources}
        self._sources_by_id: dict[str, Source] = {s.source_id: s for s in sources}

    def get_resource(self, resource_id: str) -> Resource | None:
        return self._resources_by_id.get(resource_id)

    def get_source(self, source_id: str) -> Source | None:
        return self._sources_by_id.get(source_id)

    def get_resources_by_category(self, category: str) -> list[Resource]:
        return [r for r in self.resources if r.category.value == category]

    @property
    def resource_count(self) -> int:
        return len(self.resources)

    @property
    def source_count(self) -> int:
        return len(self.sources)


def load_resource_kb(
    resources_path: str | Path,
    sources_path: str | Path,
) -> ResourceKB:
    """Load and validate the resource knowledge base from JSON files.

    Args:
        resources_path: Path to resources.json
        sources_path: Path to sources.json

    Returns:
        A validated ResourceKB instance.

    Raises:
        DataLoadError: If files are missing, malformed, or fail validation.
    """
    resources_path = Path(resources_path)
    sources_path = Path(sources_path)

    errors: list[str] = []

    # --- Load raw JSON ---
    if not resources_path.exists():
        raise DataLoadError(f"Resources file not found: {resources_path}")
    if not sources_path.exists():
        raise DataLoadError(f"Sources file not found: {sources_path}")

    try:
        with open(resources_path, encoding="utf-8") as f:
            resources_data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in resources file: {e}") from e

    try:
        with open(sources_path, encoding="utf-8") as f:
            sources_data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in sources file: {e}") from e

    # --- Validate structure ---
    if "resources" not in resources_data:
        raise DataLoadError("resources.json missing 'resources' key")
    if "sources" not in sources_data:
        raise DataLoadError("sources.json missing 'sources' key")

    dataset_version = resources_data.get("dataset_version", "unknown")

    # --- Parse sources first (needed for referential integrity) ---
    sources: list[Source] = []
    source_ids: set[str] = set()

    for i, raw_source in enumerate(sources_data["sources"]):
        try:
            source = Source(**raw_source)
            if source.source_id in source_ids:
                errors.append(f"Duplicate source_id: {source.source_id} (index {i})")
            else:
                source_ids.add(source.source_id)
                sources.append(source)
        except ValidationError as e:
            errors.append(f"Source validation error at index {i}: {e}")

    # --- Parse resources ---
    resources: list[Resource] = []
    resource_ids: set[str] = set()

    for i, raw_resource in enumerate(resources_data["resources"]):
        try:
            resource = Resource(**raw_resource)
            if resource.resource_id in resource_ids:
                errors.append(f"Duplicate resource_id: {resource.resource_id} (index {i})")
            else:
                resource_ids.add(resource.resource_id)
                resources.append(resource)
        except ValidationError as e:
            errors.append(f"Resource validation error at index {i}: {e}")

    # --- Referential integrity: every resource must reference an existing source ---
    for resource in resources:
        if resource.source_id not in source_ids:
            errors.append(
                f"Resource {resource.resource_id} references unknown source_id: {resource.source_id}"
            )

    # --- Report ---
    if errors:
        error_msg = f"Data validation failed with {len(errors)} error(s):\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        logger.error(error_msg)
        raise DataLoadError(error_msg, errors=errors)

    logger.info(
        f"Resource KB loaded: {len(resources)} resources, {len(sources)} sources, "
        f"version={dataset_version}"
    )

    return ResourceKB(
        resources=resources,
        sources=sources,
        dataset_version=dataset_version,
    )
