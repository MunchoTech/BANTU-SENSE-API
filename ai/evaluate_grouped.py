"""Evaluate Bantu-Sense with contributor-held-out cross-validation.

The source survey is read only for language and phrase-answer columns. Names,
timestamps, raw messages, and per-contributor IDs are never written to output.
"""

from __future__ import annotations

import json
import argparse
import csv
import os
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from transformers import pipeline


AI_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = AI_DIR / "raw_data.csv"
TRAIN_DATA_PATH = AI_DIR / "train.csv"
REPORT_PATH = AI_DIR / "grouped_cv_report.json"
MODEL_NAME = "Davlan/afro-xlmr-large-76L"
CLASSES = ["financial", "legal", "medical"]
N_SPLITS = 5
RANDOM_STATE = 42
ABSTENTION_THRESHOLD = 80.0
REVIEW_SAMPLE_PER_LANGUAGE_CLASS = 10


def label_for_column(column: str) -> str | None:
    name = column.lower()
    if "medical" in name or "health" in name:
        return "medical"
    if "finance" in name or "money" in name:
        return "financial"
    if "legal" in name or "rights" in name:
        return "legal"
    return None


def load_source_examples() -> tuple[list[dict], dict]:
    headers = pd.read_csv(RAW_DATA_PATH, nrows=0).columns.tolist()
    language_columns = [column for column in headers if "native language" in column.lower()]
    if len(language_columns) != 1:
        raise ValueError("Expected exactly one native-language column in raw_data.csv")

    language_column = language_columns[0]
    label_columns = [column for column in headers if label_for_column(column)]
    source = pd.read_csv(RAW_DATA_PATH, usecols=[language_column, *label_columns])
    examples = []
    speaker_languages = {}

    for speaker_id, (_, row) in enumerate(source.iterrows()):
        language = str(row[language_column]).strip().casefold()
        if language not in {"bemba", "nyanja"}:
            raise ValueError("Found a missing or unsupported contributor language")
        speaker_languages[speaker_id] = language

        for column in label_columns:
            label = label_for_column(column)
            answer = row[column]
            if pd.isna(answer):
                continue
            for phrase in re.split(r"\n|\d+\.", str(answer)):
                text = phrase.strip()
                if len(text) > 3:
                    examples.append(
                        {
                            "text": text,
                            "label": label,
                            "speaker_id": speaker_id,
                            "language": language,
                        }
                    )

    return examples, speaker_languages


def verify_source_against_training_file(examples: list[dict]) -> int:
    """Return count of untraceable train rows; fail if source rows are missing."""
    training_data = pd.read_csv(TRAIN_DATA_PATH, usecols=["text", "label"])
    source_rows = Counter((item["text"], item["label"]) for item in examples)
    train_rows = Counter(
        (str(row.text).strip(), str(row.label).strip().casefold())
        for row in training_data.itertuples(index=False)
        if pd.notna(row.text) and pd.notna(row.label)
    )

    missing_source_rows = source_rows - train_rows
    if missing_source_rows:
        raise ValueError(
            "Some source-derived phrases are absent from train.csv; resolve the data mismatch before evaluation."
        )
    return sum((train_rows - source_rows).values())


def assign_leakage_safe_groups(examples: list[dict]) -> tuple[np.ndarray, int]:
    """Keep contributors sharing an identical phrase in the same fold too."""
    parent = {}

    def find(speaker_id):
        parent.setdefault(speaker_id, speaker_id)
        if parent[speaker_id] != speaker_id:
            parent[speaker_id] = find(parent[speaker_id])
        return parent[speaker_id]

    def union(first, second):
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parent[second_root] = first_root

    speakers_by_phrase = defaultdict(set)
    for item in examples:
        normalized_text = unicodedata.normalize("NFKC", item["text"]).casefold().strip()
        speakers_by_phrase[normalized_text].add(item["speaker_id"])

    for speakers in speakers_by_phrase.values():
        speakers = sorted(speakers)
        for speaker_id in speakers[1:]:
            union(speakers[0], speaker_id)

    original_groups = {item["speaker_id"] for item in examples}
    groups = np.asarray([find(item["speaker_id"]) for item in examples])
    effective_group_count = len(set(groups.tolist()))
    merged_speakers = len(original_groups) - effective_group_count
    return groups, merged_speakers


def report_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, labels=CLASSES, average="macro", zero_division=0)), 4),
        "by_class": classification_report(
            y_true,
            y_pred,
            labels=CLASSES,
            target_names=CLASSES,
            output_dict=True,
            zero_division=0,
        ),
    }


def export_private_error_review(
    examples: list[dict],
    labels: np.ndarray,
    languages: np.ndarray,
    predictions: np.ndarray,
    confidence_percent: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    output_dir: Path,
) -> dict:
    """Write a blinded phrase sheet and separate answer key outside the repo."""
    output_dir = output_dir.expanduser().resolve()
    repo_root = AI_DIR.parent.resolve()
    if output_dir == repo_root or repo_root in output_dir.parents:
        raise ValueError("Review files must be written outside the project repository")
    errors_by_stratum = defaultdict(list)
    for index, item in enumerate(examples):
        if labels[index] != predictions[index]:
            errors_by_stratum[(languages[index], labels[index])].append(index)

    sampler = random.Random(RANDOM_STATE)
    selected = []
    selected_counts = {}
    for language in sorted(set(languages.tolist())):
        for label in CLASSES:
            candidates = errors_by_stratum.get((language, label), []).copy()
            sampler.shuffle(candidates)
            chosen = candidates[:REVIEW_SAMPLE_PER_LANGUAGE_CLASS]
            selected.extend(chosen)
            selected_counts[f"{language}:{label}"] = len(chosen)
    sampler.shuffle(selected)

    fold_by_index = np.zeros(len(examples), dtype=int)
    for fold_number, (_, test_indices) in enumerate(folds, start=1):
        fold_by_index[test_indices] = fold_number

    output_dir.mkdir(parents=True, exist_ok=True)
    review_path = output_dir / "review_blind.csv"
    key_path = output_dir / "review_answer_key.csv"
    review_fields = [
        "sample_id",
        "language",
        "phrase",
        "reviewer_language_check",
        "reviewer_intent_label",
        "reviewer_naturalness",
        "reviewer_ambiguity_or_context_notes",
    ]
    key_fields = [
        "sample_id",
        "fold",
        "language",
        "dataset_label_from_survey_prompt",
        "model_prediction",
        "model_confidence_percent_uncalibrated",
    ]

    def open_private_csv(path: Path):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.fchmod(descriptor, 0o600)
        return os.fdopen(descriptor, "w", newline="", encoding="utf-8")

    with open_private_csv(review_path) as review_file, open_private_csv(key_path) as key_file:
        review_writer = csv.DictWriter(review_file, fieldnames=review_fields)
        key_writer = csv.DictWriter(key_file, fieldnames=key_fields)
        review_writer.writeheader()
        key_writer.writeheader()

        for sequence, index in enumerate(selected, start=1):
            sample_id = f"ERR-{sequence:03d}"
            review_writer.writerow(
                {
                    "sample_id": sample_id,
                    "language": languages[index],
                    "phrase": examples[index]["text"],
                    "reviewer_language_check": "",
                    "reviewer_intent_label": "",
                    "reviewer_naturalness": "",
                    "reviewer_ambiguity_or_context_notes": "",
                }
            )

            key_writer.writerow(
                {
                    "sample_id": sample_id,
                    "fold": fold_by_index[index],
                    "language": languages[index],
                    "dataset_label_from_survey_prompt": labels[index],
                    "model_prediction": predictions[index],
                    "model_confidence_percent_uncalibrated": round(
                        float(confidence_percent[index]), 2
                    ),
                }
            )

    return {
        "review_rows": len(selected),
        "max_per_language_class": REVIEW_SAMPLE_PER_LANGUAGE_CLASS,
        "selected_errors_by_language_and_dataset_label": selected_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-review-sheet",
        action="store_true",
        help="Export a small blinded error-review sheet to a local directory outside the repository.",
    )
    parser.add_argument(
        "--review-output-dir",
        type=Path,
        default=Path("/tmp/bantu-sense-review"),
        help="Private local output directory used with --export-review-sheet (default: /tmp/bantu-sense-review).",
    )
    args = parser.parse_args()

    examples, speaker_languages = load_source_examples()
    untraceable_train_rows = verify_source_against_training_file(examples)
    groups, merged_speakers = assign_leakage_safe_groups(examples)

    texts = [item["text"] for item in examples]
    labels = np.asarray([item["label"] for item in examples])
    languages = np.asarray([item["language"] for item in examples])
    normalized_texts = [
        unicodedata.normalize("NFKC", text).casefold().strip() for text in texts
    ]

    splitter = StratifiedGroupKFold(
        n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE
    )
    fold_strata = np.asarray(
        [f"{language}:{label}" for language, label in zip(languages, labels)]
    )
    folds = list(splitter.split(np.zeros(len(examples)), fold_strata, groups))
    predictions = np.empty(len(examples), dtype=object)
    confidence_percent = np.zeros(len(examples), dtype=float)
    balanced_predictions = np.empty(len(examples), dtype=object)
    balanced_confidence_percent = np.zeros(len(examples), dtype=float)
    fold_summaries = []

    print(f"Loading frozen encoder: {MODEL_NAME}", flush=True)
    extractor = pipeline("feature-extraction", model=MODEL_NAME)
    embeddings = []
    for index, text in enumerate(texts, start=1):
        # Match the serving/training path: truncate to 512 characters, then
        # use the first token's feature vector.
        embeddings.append(extractor(text[:512])[0][0])
        if index % 50 == 0 or index == len(texts):
            print(f"Extracted anonymous phrase features: {index}/{len(texts)}", flush=True)
    features = np.asarray(embeddings)

    for fold_number, (train_indices, test_indices) in enumerate(folds, start=1):
        train_groups = set(groups[train_indices].tolist())
        test_groups = set(groups[test_indices].tolist())
        if train_groups & test_groups:
            raise AssertionError("Contributor leakage detected between train and test fold")
        if set(normalized_texts[index] for index in train_indices) & set(
            normalized_texts[index] for index in test_indices
        ):
            raise AssertionError("Exact phrase leakage detected between train and test fold")

        model_settings = [
            ("baseline", None, predictions, confidence_percent),
            ("class_weight_balanced", "balanced", balanced_predictions, balanced_confidence_percent),
        ]
        for _, class_weight, prediction_store, confidence_store in model_settings:
            classifier = LogisticRegression(max_iter=1000, class_weight=class_weight)
            classifier.fit(features[train_indices], labels[train_indices])
            fold_probabilities = classifier.predict_proba(features[test_indices])
            fold_predictions = classifier.classes_[fold_probabilities.argmax(axis=1)]
            prediction_store[test_indices] = fold_predictions
            confidence_store[test_indices] = fold_probabilities.max(axis=1) * 100

        language_counts = Counter(languages[test_indices].tolist())
        fold_summaries.append(
            {
                "fold": fold_number,
                "held_out_contributors": len(test_groups),
                "held_out_phrases": len(test_indices),
                "held_out_phrases_by_language": dict(language_counts),
            }
        )
        print(
            f"Completed fold {fold_number}/{N_SPLITS}: "
            f"{len(test_groups)} held-out contributors, {len(test_indices)} phrases",
            flush=True,
        )

    overall_metrics = report_metrics(labels, predictions)
    balanced_overall_metrics = report_metrics(labels, balanced_predictions)
    per_language_metrics = {
        language: report_metrics(labels[languages == language], predictions[languages == language])
        for language in sorted(set(languages.tolist()))
    }
    balanced_per_language_metrics = {
        language: report_metrics(
            labels[languages == language], balanced_predictions[languages == language]
        )
        for language in sorted(set(languages.tolist()))
    }

    def abstention_summary(model_predictions, model_confidence):
        accepted = model_confidence >= ABSTENTION_THRESHOLD
        accepted_count = int(accepted.sum())
        selective_accuracy = (
            float(accuracy_score(labels[accepted], model_predictions[accepted]))
            if accepted_count
            else None
        )
        return {
            "accepted_phrases": accepted_count,
            "coverage": round(float(accepted.mean()), 4),
            "accuracy_on_accepted": (
                round(selective_accuracy, 4) if selective_accuracy is not None else None
            ),
            "abstained_phrases": int((~accepted).sum()),
        }

    baseline_legal_recall = overall_metrics["by_class"]["legal"]["recall"]
    balanced_legal_recall = balanced_overall_metrics["by_class"]["legal"]["recall"]
    baseline_nyanja_legal_recall = per_language_metrics["nyanja"]["by_class"]["legal"]["recall"]
    balanced_nyanja_legal_recall = balanced_per_language_metrics["nyanja"]["by_class"]["legal"]["recall"]
    majority_label = Counter(labels.tolist()).most_common(1)[0][0]
    private_review_export = None
    if args.export_review_sheet:
        private_review_export = export_private_error_review(
            examples,
            labels,
            languages,
            predictions,
            confidence_percent,
            folds,
            args.review_output_dir,
        )

    report = {
        "evaluation": "5-fold stratified grouped cross-validation",
        "fold_stratification": "combined language and intent label",
        "random_seed": RANDOM_STATE,
        "encoder": MODEL_NAME,
        "baseline_classifier": "LogisticRegression(max_iter=1000)",
        "comparison_classifier": "LogisticRegression(max_iter=1000, class_weight='balanced')",
        "feature_extraction": "same as current serving path: text[:512], first token vector",
        "source_contributors": len(speaker_languages),
        "effective_groups_after_exact_phrase_leakage_control": len(set(groups.tolist())),
        "contributors_grouped_together_due_to_shared_exact_phrases": merged_speakers,
        "source_derived_phrases_evaluated": len(examples),
        "train_csv_rows_without_source_contributor_mapping_excluded": untraceable_train_rows,
        "language_counts": dict(Counter(languages.tolist())),
        "class_counts": dict(Counter(labels.tolist())),
        "majority_class_baseline": {
            "class": majority_label,
            "accuracy": round(float(np.mean(labels == majority_label)), 4),
        },
        "overall": overall_metrics,
        "confusion_matrix_class_order": CLASSES,
        "confusion_matrix_rows_actual_columns_predicted": confusion_matrix(
            labels, predictions, labels=CLASSES
        ).tolist(),
        "by_language": per_language_metrics,
        "current_80_percent_abstention_threshold": {
            **abstention_summary(predictions, confidence_percent),
        },
        "class_weight_balanced": {
            "overall": balanced_overall_metrics,
            "confusion_matrix_rows_actual_columns_predicted": confusion_matrix(
                labels, balanced_predictions, labels=CLASSES
            ).tolist(),
            "by_language": balanced_per_language_metrics,
            "current_80_percent_abstention_threshold": abstention_summary(
                balanced_predictions, balanced_confidence_percent
            ),
        },
        "comparison_deltas_balanced_minus_baseline": {
            "accuracy": round(
                balanced_overall_metrics["accuracy"] - overall_metrics["accuracy"], 4
            ),
            "macro_f1": round(
                balanced_overall_metrics["macro_f1"] - overall_metrics["macro_f1"], 4
            ),
            "legal_recall": round(balanced_legal_recall - baseline_legal_recall, 4),
            "nyanja_legal_recall": round(
                balanced_nyanja_legal_recall - baseline_nyanja_legal_recall, 4
            ),
        },
        "folds": fold_summaries,
        "limitations": [
            "Only 24 survey contributors are available; estimates may vary with new contributors.",
            "Eight train.csv rows have no matching source contributor and are excluded from all folds.",
            "Confidence percentages are classifier outputs and have not been calibrated.",
            "This evaluates intent classification only; it does not evaluate translation or urgency.",
        ],
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nAggregate grouped evaluation (no message text or names):\n{json.dumps(report, indent=2)}")
    print(f"\nSaved aggregate report to {REPORT_PATH}")
    if args.export_review_sheet:
        review_dir = args.review_output_dir.expanduser().resolve()
        print(f"Private review rows selected: {private_review_export['review_rows']}")
        print(
            "Selected per language and dataset label: "
            f"{json.dumps(private_review_export['selected_errors_by_language_and_dataset_label'])}"
        )
        print(f"\nPrivate blinded review sheet: {review_dir / 'review_blind.csv'}")
        print(f"Separate answer key: {review_dir / 'review_answer_key.csv'}")


if __name__ == "__main__":
    main()
