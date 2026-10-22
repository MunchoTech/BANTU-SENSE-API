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
        self.main.clf.predict_proba = lambda _features: [[0.55, 0.45]]

    def tearDown(self):
        self.env_patch.stop()

    def test_uncertain_message_is_not_stored_without_opt_in(self):
        result = asyncio.run(self.main.predict_intent(self.main.UserInput(text="sample")))

        self.assertEqual(result["status"], "uncertain")
        self.assertFalse(result["reviewSubmitted"])
        self.assertEqual(result["status"], "uncertain")
        self.assertEqual(result["urgencyScore"], 5)
        self.assertEqual(result["urgencyLevel"], "ROUTINE")
        self.assertIsNone(result["semanticContext"])
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

            self.assertTrue(result["reviewSubmitted"])
            self.assertTrue(log_path.is_file())
            self.assertIn("sample", log_path.read_text(encoding="utf-8"))

    def test_opt_in_without_configured_log_does_not_claim_submission(self):
        result = asyncio.run(
            self.main.predict_intent(
                self.main.UserInput(text="sample", donate_for_review=True)
            )
        )

        self.assertFalse(result["reviewSubmitted"])
        self.assertIn("not stored", result["message"])

    def test_camel_case_review_opt_in_is_accepted_for_api_clients(self):
        request = self.main.UserInput.model_validate(
            {"text": "sample", "donateForReview": True}
        )

        self.assertTrue(request.donate_for_review)

    def test_analyzed_result_uses_the_same_contract(self):
        self.main.clf.predict_proba = lambda _features: [[0.91, 0.09]]
        result = asyncio.run(
            self.main.predict_intent(
                self.main.UserInput(text="Mwana wanga akudwala kwambiri, help.")
            )
        )

        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(result["intent"], "MEDICAL")
        self.assertIsInstance(result["confidence"], float)
        self.assertEqual(result["urgencyScore"], 9)
        self.assertEqual(result["urgencyLevel"], "CRITICAL")
        self.assertFalse(result["reviewSubmitted"])
        self.assertIsInstance(result["semanticContext"], str)
        self.assertEqual(
            set(result),
            {
                "status",
                "intent",
                "confidence",
                "urgencyScore",
                "urgencyLevel",
                "reviewSubmitted",
                "message",
                "semanticContext",
            },
        )


if __name__ == "__main__":
    unittest.main()
