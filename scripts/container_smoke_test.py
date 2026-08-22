from __future__ import annotations

import sys
import urllib.request


def check(path: str) -> None:
    with urllib.request.urlopen(
        f"http://127.0.0.1:8000{path}",
        timeout=5,
    ) as response:
        if response.status != 200:
            raise RuntimeError(f"{path} returned HTTP {response.status}")


def main() -> None:
    check("/health")
    check("/ready")
    print("Container smoke test passed.")


if __name__ == "__main__":
    sys.exit(main())
