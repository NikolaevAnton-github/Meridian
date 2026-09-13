-- Preserve existing UUIDs and spelling. Refuse case-only duplicate paths even
-- after a file has been renamed on disk or through direct registry SQL writes.
CREATE UNIQUE INDEX artifacts_path_case_insensitive
    ON asset_registry.artifacts (lower(path));
