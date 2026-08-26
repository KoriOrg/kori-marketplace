import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print(
        "Missing dependency: jsonschema\n"
        "Install it with: python3 -m pip install jsonschema",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schema" / "v1"

SCHEMA_BY_ID = {
    "kori.marketplace.index.v1": "index.json",
    "kori.package.v1": "package.json",
    "kori.publisher.v1": "publisher.json",
    "kori.trust.v1": "trust.json",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValueError(f"{path}: invalid JSON: {err}") from err


def schema_path_for(manifest: dict[str, Any], explicit_schema: str | None) -> Path:
    if explicit_schema:
        path = Path(explicit_schema)
        if not path.is_absolute():
            path = ROOT / path
        return path

    schema_id = manifest.get("schema")
    if not isinstance(schema_id, str):
        raise ValueError("manifest must contain a string 'schema' field")

    filename = SCHEMA_BY_ID.get(schema_id)
    if filename is None:
        known = ", ".join(sorted(SCHEMA_BY_ID))
        raise ValueError(f"unknown schema '{schema_id}', known schemas: {known}")

    return SCHEMAS / filename


def validate(manifest_path: Path, explicit_schema: str | None) -> None:
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be a JSON object")

    schema_path = schema_path_for(manifest, explicit_schema)
    schema = load_json(schema_path)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda err: list(err.path))
    if errors:
        for err in errors:
            path = ".".join(str(part) for part in err.absolute_path) or "<root>"
            print(f"{manifest_path}: {path}: {err.message}", file=sys.stderr)
        raise SystemExit(1)

    print(f"ok: {manifest_path} matches {schema_path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a Kori JSON manifest against its JSON Schema.",
    )
    parser.add_argument("manifest", help="Path to the JSON manifest to validate.")
    parser.add_argument(
        "--schema",
        help="Optional explicit schema path, relative to marketplace root or absolute.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = Path.cwd() / manifest_path

    try:
        validate(manifest_path, args.schema)
    except ValueError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1) from err


if __name__ == "__main__":
    main()
