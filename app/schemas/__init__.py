"""Pydantic models shared by the API and persistence layers.

Fields are snake_case in Python and MongoDB, and camelCase on the wire — matching the
frontend's `src/types/index.ts` — via the alias generator on `CamelModel`.
"""
