from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILES = (".env", ".env.local", ".env.dev.local")


def load_prefixed_env(prefix: str, root: Path | None = None) -> dict[str, str]:
    root = root or ROOT
    values: dict[str, str] = {}
    for name in ENV_FILES:
        path = root / name
        if path.exists():
            values.update(parse_env_file(path, prefix=prefix))

    for key, value in os.environ.items():
        if key.startswith(prefix):
            values[key] = value
    return values


def load_prefixed_env_with_legacy_aliases(
    preferred_prefix: str,
    legacy_prefixes: tuple[str, ...],
    root: Path | None = None,
) -> dict[str, str]:
    values: dict[str, str] = {}
    for legacy_prefix in legacy_prefixes:
        legacy_values = load_prefixed_env(legacy_prefix, root=root)
        values.update(_normalize_prefixed_env(legacy_values, legacy_prefix, preferred_prefix))

    values.update(load_prefixed_env(preferred_prefix, root=root))
    return values


def _normalize_prefixed_env(values: dict[str, str], source_prefix: str, target_prefix: str) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in values.items():
        if key.startswith(source_prefix):
            normalized[target_prefix + key[len(source_prefix) :]] = value
    return normalized


def parse_env_file(path: Path, prefix: str | None = None) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if prefix is not None and not key.startswith(prefix):
            continue
        values[key] = strip_env_value(value.strip())
    return values


def strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
