# tests/test_pipeline.py
# End-to-end pipeline test that mocks all Groq API calls.
# Run from the project root:
#   python tests/test_pipeline.py
#
# Tests covered:
#   1. Municipality lookup (data layer)
#   2. Department email lookup (data layer)
#   3. Classification output validation (service logic)
#   4. Full upload pipeline  — mocked AI services, in-memory DB
#   5. GET /complaints pagination
#   6. GET /complaints/{id} detail + 404

import io
import json
import os
import struct
import sys
import unittest
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# Ensure project root is on the path and env vars are set FIRST
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.environ["GROQ_API_KEY"]   = "gsk_test_dummy_key_not_real"
os.environ["EMAIL_SENDER"]   = ""
os.environ["EMAIL_PASSWORD"] = ""


# ---------------------------------------------------------------------------
# Helper: minimal valid WAV (44-byte header, no audio data)
# ---------------------------------------------------------------------------
def _make_wav_bytes() -> bytes:
    """Return a minimal valid WAV file as bytes."""
    data_bytes = b""
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + len(data_bytes), b"WAVE",
        b"fmt ", 16, 1, 1, 44100, 88200, 2, 16,
        b"data", len(data_bytes),
    )
    return header + data_bytes


# ---------------------------------------------------------------------------
# Fake pipeline responses
# ---------------------------------------------------------------------------
MOCK_TRANSCRIPTION = "Има дупка на улица Витоша в Ботевград. Много е опасно."

MOCK_CLASSIFICATION_RESULT = {
    "category": "ROADS",
    "location_mentioned": "ботевград",
    "urgency": "HIGH",
}

MOCK_FORMAL_LETTER = (
    "ДО: Отдел Пътна инфраструктура и транспорт\n"
    "ОБЩИНА: Ботевград\n\n"
    "ОТНОСНО: Сигнал за пътна инфраструктура\n\n"
    "УВАЖАЕМИ ДАМИ И ГОСПОДА,\n\n"
    "Гражданин от Ботевград сигнализира за опасна дупка.\n\n"
    "С уважение,\nГражданин на Ботевград\nДата: 11.04.2026"
)


# ---------------------------------------------------------------------------
# Shared test setup: TestClient + isolated in-memory SQLite
# ---------------------------------------------------------------------------

def _make_test_client():
    """Return (TestClient, app) with an isolated in-memory database.

    The key trick: we patch backend.database.engine and recreate all tables
    against the in-memory engine BEFORE the app processes any request, so
    the Complaint model is mapped to the right engine.
    """
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient

    # Build an isolated in-memory engine
    mem_engine = sqlalchemy.create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=mem_engine)

    # Import models and Base AFTER env vars are set, create tables
    from backend.database import Base, get_db
    from backend import models  # noqa: F401 — registers Complaint on Base
    Base.metadata.create_all(bind=mem_engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    from backend.main import app
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, raise_server_exceptions=False)
    return client, app


# ---------------------------------------------------------------------------
# 1. Municipality lookup
# ---------------------------------------------------------------------------

class TestMunicipalityLookup(unittest.TestCase):
    """Unit tests for backend/data/municipalities.py."""

    def setUp(self):
        from backend.data.municipalities import lookup_municipality
        self.lookup = lookup_municipality

    def test_exact_match(self):
        r = self.lookup("ботевград")
        self.assertIsNotNone(r)
        self.assertEqual(r["municipality"], "Ботевград")

    def test_case_insensitive(self):
        r = self.lookup("СВОГЕ")
        self.assertIsNotNone(r)
        self.assertEqual(r["municipality"], "Своге")

    def test_leading_trailing_whitespace(self):
        self.assertIsNotNone(self.lookup("  своге  "))

    def test_village_resolves_to_municipality(self):
        r = self.lookup("владо тричков")
        self.assertEqual(r["municipality"], "Своге")

    def test_unknown_returns_none(self):
        self.assertIsNone(self.lookup("несъществуващо"))

    def test_none_input_returns_none(self):
        self.assertIsNone(self.lookup(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(self.lookup(""))


# ---------------------------------------------------------------------------
# 2. Department email lookup
# ---------------------------------------------------------------------------

class TestDepartmentEmails(unittest.TestCase):
    """Unit tests for backend/data/department_emails.py."""

    def setUp(self):
        from backend.data.department_emails import get_department_email, DEPARTMENT_EMAILS
        self.get = get_department_email
        self.all = DEPARTMENT_EMAILS

    def test_known_category_and_municipality(self):
        self.assertEqual(self.get("ROADS", "Ботевград"), "roads@botevgrad.bg")

    def test_known_category_water_svoge(self):
        self.assertEqual(self.get("WATER_SUPPLY", "Своге"), "water@svoge.bg")

    def test_fallback_to_default_on_unknown_municipality(self):
        self.assertEqual(self.get("WATER_SUPPLY", "Непознато"), "water@municipality.bg")

    def test_none_municipality_uses_default(self):
        self.assertEqual(self.get("ELECTRICITY", None), "electricity@municipality.bg")

    def test_unknown_category_returns_other_default(self):
        email = self.get("NONEXISTENT_CATEGORY", None)
        self.assertIn("@", email)

    def test_all_categories_have_default_key(self):
        for cat, mapping in self.all.items():
            self.assertIn("default", mapping, f"Category '{cat}' missing 'default' key")


# ---------------------------------------------------------------------------
# 3. Classification validation
# ---------------------------------------------------------------------------

class TestClassificationValidation(unittest.TestCase):
    """Unit tests for the output normalisation in classification service."""

    def setUp(self):
        from backend.services.classification import _validate_and_normalise
        self.validate = _validate_and_normalise

    def test_invalid_category_becomes_other(self):
        r = self.validate({"category": "GARBAGE", "urgency": "HIGH", "location_mentioned": None})
        self.assertEqual(r["category"], "OTHER")

    def test_all_valid_categories_pass_through(self):
        for cat in ["WATER_SUPPLY","ELECTRICITY","ROADS","WASTE_MANAGEMENT",
                    "PUBLIC_ORDER","GREEN_SPACES","ADMINISTRATIVE","OTHER"]:
            r = self.validate({"category": cat, "urgency": "LOW", "location_mentioned": None})
            self.assertEqual(r["category"], cat)

    def test_invalid_urgency_becomes_medium(self):
        r = self.validate({"category": "ROADS", "urgency": "CRITICAL", "location_mentioned": None})
        self.assertEqual(r["urgency"], "MEDIUM")

    def test_location_lowercased(self):
        r = self.validate({"category": "ROADS", "urgency": "HIGH", "location_mentioned": "Ботевград"})
        self.assertEqual(r["location_mentioned"], "ботевград")

    def test_empty_location_becomes_none(self):
        r = self.validate({"category": "ROADS", "urgency": "HIGH", "location_mentioned": "   "})
        self.assertIsNone(r["location_mentioned"])


# ---------------------------------------------------------------------------
# 4–6. Full pipeline integration tests
# ---------------------------------------------------------------------------

_PIPELINE_PATCHES = [
    patch("backend.services.transcription.transcribe_audio",
          new_callable=AsyncMock, return_value=MOCK_TRANSCRIPTION),
    patch("backend.services.classification.classify_complaint",
          new_callable=AsyncMock, return_value=MOCK_CLASSIFICATION_RESULT),
    patch("backend.services.formalization.formalize_complaint",
          new_callable=AsyncMock, return_value=MOCK_FORMAL_LETTER),
    patch("backend.services.email_service.send_complaint_email", return_value=False),
]


def _apply_patches(test_func):
    """Stack all four pipeline mock patches on a test method."""
    for p in reversed(_PIPELINE_PATCHES):
        test_func = p(test_func)
    return test_func


class TestFullPipeline(unittest.TestCase):
    """Integration tests for all /complaints endpoints with mocked AI."""

    def setUp(self):
        self.client, self.app = _make_test_client()

    def tearDown(self):
        self.app.dependency_overrides.clear()

    @_apply_patches
    def test_upload_full_success(self, *_mocks):
        """Full pipeline returns success JSON with all expected fields."""
        r = self.client.post(
            "/complaints/upload",
            files={"audio_file": ("test.wav", io.BytesIO(_make_wav_bytes()), "audio/wav")},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["status"], "success", data)
        self.assertEqual(data["transcribed_text"], MOCK_TRANSCRIPTION)
        self.assertEqual(data["category"], "ROADS")
        self.assertEqual(data["urgency"], "HIGH")
        self.assertEqual(data["municipality"], "Ботевград")
        self.assertEqual(data["sent_to_email"], "roads@botevgrad.bg")
        self.assertFalse(data["email_sent"])
        self.assertIsInstance(data["complaint_id"], int)

    @patch("backend.services.transcription.transcribe_audio",
           new_callable=AsyncMock,
           side_effect=RuntimeError("Groq Whisper transcription failed after retry."))
    def test_upload_transcription_failure(self, _mock):
        """When transcription raises, pipeline returns error at step 'transcription'."""
        r = self.client.post(
            "/complaints/upload",
            files={"audio_file": ("fail.wav", io.BytesIO(_make_wav_bytes()), "audio/wav")},
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["step_failed"], "transcription")

    def test_upload_missing_file_returns_422(self):
        """POST without file body returns HTTP 422."""
        r = self.client.post("/complaints/upload")
        self.assertEqual(r.status_code, 422)

    @_apply_patches
    def test_get_complaints_pagination(self, *_mocks):
        """GET /complaints returns paginated results with correct total."""
        wav = _make_wav_bytes()
        for _ in range(3):
            self.client.post(
                "/complaints/upload",
                files={"audio_file": ("t.wav", io.BytesIO(wav), "audio/wav")},
            )
        r = self.client.get("/complaints?page=1&limit=2")
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertEqual(data["total"], 3)
        self.assertEqual(len(data["items"]), 2)
        # Page 2 has the last item
        r2 = self.client.get("/complaints?page=2&limit=2")
        self.assertEqual(len(r2.json()["items"]), 1)

    @_apply_patches
    def test_get_complaint_by_id(self, *_mocks):
        """GET /complaints/{id} returns detail including formal_letter."""
        upload_r = self.client.post(
            "/complaints/upload",
            files={"audio_file": ("t.wav", io.BytesIO(_make_wav_bytes()), "audio/wav")},
        )
        self.assertEqual(upload_r.status_code, 200, upload_r.text)
        complaint_id = upload_r.json()["complaint_id"]

        detail_r = self.client.get(f"/complaints/{complaint_id}")
        self.assertEqual(detail_r.status_code, 200)
        detail = detail_r.json()
        self.assertIn("formal_letter", detail)
        self.assertEqual(detail["category"], "ROADS")
        self.assertEqual(detail["urgency"], "HIGH")
        self.assertEqual(detail["location_mentioned"], "ботевград")

    def test_get_complaint_unknown_id_returns_404(self):
        """GET /complaints/{id} returns 404 for unknown id."""
        r = self.client.get("/complaints/99999")
        self.assertEqual(r.status_code, 404)

    def test_health_check(self):
        """GET / returns {status: ok}."""
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("Smart Box — Backend Pipeline Test Suite")
    print("=" * 65)
    unittest.main(verbosity=2)
