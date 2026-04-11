# backend/app/database.py
# Compatibility shim — delegates to the canonical backend/database.py.
# Kept so that any code still importing from backend.app.database continues
# to work without changes.

from backend.database import Base, engine, SessionLocal, get_db  # noqa: F401
