import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / "packages"
SCHEMAS = ROOT / "schema"
INDEX = ROOT / "index.json"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_publishers() -> list[dict]:
    publishers = []
    for path in sorted(PACKAGES.glob("*/publisher.json")):
        manifest = load_json(path)
        publishers.append(
            {
                "id": manifest["id"],
                "manifest": relative(path),
            }
        )
    return publishers


def discover_packages() -> list[dict]:
    packages = []
    for path in sorted(PACKAGES.glob("*/*/*/package.json")):
        manifest = load_json(path)
        packages.append(
            {
                "id": manifest["id"],
                "name": manifest["name"],
                "description": manifest["description"],
                "publisher": manifest["publisher"],
                "latest": manifest["version"],
                "manifest": relative(path),
            }
        )
    return packages


def discover_schemas() -> list[dict]:
    schemas = []
    for path in sorted(SCHEMAS.glob("**/*.json")):
        schema = load_json(path)
        schemas.append(
            {
                "id": schema["properties"]["schema"]["const"],
                "path": relative(path),
            }
        )
    return schemas


def main() -> None:
    index = {
        "schema": "kori.marketplace.index.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "trust": "packages/trust.json",
        "schemas": discover_schemas(),
        "publishers": discover_publishers(),
        "packages": discover_packages(),
    }
    INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
