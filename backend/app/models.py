# backend/app/models.py
# Compatibility shim — re-exports the canonical Complaint model from
# backend.models so that any code importing from backend.app.models continues
# to work without redeclaring the table (which would cause an SQLAlchemy
# mapping conflict).

from backend.models import Complaint  # noqa: F401
