"""Shared fixtures for all test layers."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

# Ensure src is importable
os.environ.setdefault("PYTHONPATH", str(Path(__file__).resolve().parent.parent / "src"))

from emomcp.infrastructure.sqlite_repositories import DatabaseConnection


@pytest.fixture(scope="session")
def db_path():
    """Return path to the real emotions.db shipped with the project."""
    p = Path(__file__).resolve().parent.parent / "config" / "emotions.db"
    assert p.exists(), f"Database not found at {p}"
    return str(p)


@pytest.fixture(scope="session")
def db(db_path):
    """Provide a DatabaseConnection for all tests (read-only)."""
    conn = DatabaseConnection(db_path)
    yield conn
    conn.close()


@pytest.fixture
def raw_conn(db_path):
    """Provide a raw sqlite3 connection for low-level assertions."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
