import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / "packages"
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
                "publisher": manifest["publisher"],
                "latest": manifest["version"],
                "manifest": relative(path),
            }
        )
    return packages


def main() -> None:
    index = {
        "schema": "kori.marketplace.index.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "trust": "packages/trust.json",
        "publishers": discover_publishers(),
        "packages": discover_packages(),
    }
    INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
