import asyncio
import importlib
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeExtractor:
    def __call__(self, _text):
        return [[[0.0] * 1024]]


class FakeClassifier:
    def predict(self, _features):
        return ["medical"]

    def predict_proba(self, _features):
        return [([0.55, 0.45])]


class ReviewConsentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(__file__).parent))
        fake_transformers = types.ModuleType("transformers")
        fake_transformers.pipeline = lambda *_args, **_kwargs: FakeExtractor()
        with patch.dict(sys.modules, {"transformers": fake_transformers}), patch(
            "joblib.load", return_value=FakeClassifier()
        ):
            cls.main = importlib.import_module("main")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("main", None)
        sys.path.remove(str(Path(__file__).parent))

    def setUp(self):
        self.env_patch = patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()

    def test_uncertain_message_is_not_stored_without_opt_in(self):
        result = asyncio.run(self.main.predict_intent(self.main.UserInput(text="sample")))

        self.assertEqual(result["status"], "uncertain")
        self.assertFalse(result["review_submitted"])
        self.assertIn("urgency_score", result)
        self.assertNotIn("urgency", result)
        self.assertIn("not stored", result["message"])

    def test_opted_in_message_is_stored_only_at_configured_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "reviews" / "candidates.csv"
            os.environ["BANTU_REVIEW_LOG_PATH"] = str(log_path)

            result = asyncio.run(
                self.main.predict_intent(
                    self.main.UserInput(text="sample", donate_for_review=True)
                )
            )

            self.assertTrue(result["review_submitted"])
            self.assertTrue(log_path.is_file())
            self.assertIn("sample", log_path.read_text(encoding="utf-8"))

    def test_opt_in_without_configured_log_does_not_claim_submission(self):
        result = asyncio.run(
            self.main.predict_intent(
                self.main.UserInput(text="sample", donate_for_review=True)
            )
        )

        self.assertFalse(result["review_submitted"])
        self.assertIn("not stored", result["message"])


if __name__ == "__main__":
    unittest.main()
