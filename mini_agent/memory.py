from __future__ import annotations

from pathlib import Path


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        return [line.strip() for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append(self, item: str) -> None:
        with self.path.open("a", encoding="utf-8") as file:
            file.write(item.strip() + "\n")

