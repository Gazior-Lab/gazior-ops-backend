"""Pytest configuration: ensure settings load without a real .env in CI/local."""

import os

# Must run before importing app.*
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/gazior_ops_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("APP_ENV", "test")
