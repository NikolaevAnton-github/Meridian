CREATE SCHEMA asset_registry;
CREATE TABLE asset_registry.assets (
    id uuid PRIMARY KEY,
    name text NOT NULL UNIQUE
);
CREATE TABLE asset_registry.artifacts (
    id uuid PRIMARY KEY,
    asset_id uuid NOT NULL REFERENCES asset_registry.assets(id),
    path text NOT NULL UNIQUE CHECK (path !~ '(^/|\\|(^|/)\.\.(/|$)|:)'),
    role text NOT NULL,
    sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
    unreal_package text,
    evidence jsonb NOT NULL
);
CREATE TABLE asset_registry.dependencies (
    upstream uuid NOT NULL REFERENCES asset_registry.artifacts(id),
    downstream uuid NOT NULL REFERENCES asset_registry.artifacts(id),
    kind text NOT NULL,
    status text NOT NULL CHECK (status IN ('verified', 'declared', 'unverified')),
    evidence jsonb NOT NULL,
    PRIMARY KEY (upstream, downstream, kind),
    CHECK (upstream <> downstream)
);
CREATE INDEX ON asset_registry.dependencies(downstream);
