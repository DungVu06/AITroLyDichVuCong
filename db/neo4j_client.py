"""Reusable Neo4j client for application code and ad-hoc queries."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

try:
    from neo4j import Driver, GraphDatabase
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Thiếu neo4j driver. Cài bằng: python3 -m pip install neo4j"
    ) from exc

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    """Load simple KEY=VALUE entries without overwriting env vars."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Neo4jClient:
    """Small wrapper around the official Neo4j driver."""

    def __init__(self, driver: Driver, database: str = "neo4j") -> None:
        self.driver = driver
        self.database = database

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Neo4jClient":
        load_dotenv(env_file or PROJECT_ROOT / ".env")
        uri = os.getenv("NEO4J_URI", "").strip()
        username = os.getenv("NEO4J_USERNAME", "neo4j").strip()
        password = os.getenv("NEO4J_PASSWORD", "")
        database = os.getenv("NEO4J_DATABASE", "neo4j").strip() or "neo4j"
        missing = [name for name, value in (("NEO4J_URI", uri), ("NEO4J_PASSWORD", password)) if not value]
        if missing:
            raise ValueError(f"Thiếu cấu hình Neo4j: {', '.join(missing)}")
        return cls(GraphDatabase.driver(uri, auth=(username, password)), database)

    def verify_connectivity(self) -> None:
        self.driver.verify_connectivity()

    def query(self, cypher: str, parameters: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a read query and return rows as ordinary dictionaries."""
        with self.driver.session(database=self.database) as session:
            return [record.data() for record in session.run(cypher, parameters or {})]

    def execute(self, cypher: str, parameters: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Run a write query and return useful summary counters."""
        with self.driver.session(database=self.database) as session:
            counters = session.run(cypher, parameters or {}).consume().counters
            return {
                "nodes_created": counters.nodes_created,
                "nodes_deleted": counters.nodes_deleted,
                "relationships_created": counters.relationships_created,
                "relationships_deleted": counters.relationships_deleted,
                "properties_set": counters.properties_set,
            }

    def close(self) -> None:
        self.driver.close()

    def __enter__(self) -> "Neo4jClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

