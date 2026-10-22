# Bantu-Sense intent evaluation

**Run date:** 2026-10-22

**Evaluation:** 5-fold grouped cross-validation by survey contributor
**Detailed aggregate output:** [`grouped_cv_report.json`](grouped_cv_report.json)

## Result

I compared the current Logistic Regression head with `class_weight="balanced"` using the same frozen Afro-XLM-R features and the same five contributor-held-out folds. The majority-class baseline is **35.1%**.

| Measure | Current classifier | Class-weighted |
| --- | ---: | ---: |
| Overall accuracy | 63.2% | 63.5% |
| Overall macro F1 | 63.2% | 63.4% |
| Legal recall, both languages | 59.8% | 60.6% |
| Legal recall, Bemba | 65.0% | 66.7% |
| Legal recall, Nyanja | 55.2% | 55.2% |
| Bemba accuracy | 68.6% | 69.6% |
| Nyanja accuracy | 58.6% | 58.1% |

Class weighting changes overall accuracy by **0.2 percentage points** and macro F1 by **0.3 points**. Legal recall rises by **0.8 points overall**, entirely in Bemba; Nyanja legal recall does not change. Nyanja accuracy drops by about **0.5 points**. This is too small and uneven to justify changing the production classifier. The class-weighted model is an experiment only; the saved model was not replaced.

Both versions still make substantial errors. Legal intent remains the weakest category, particularly for Nyanja. With the current classifier, 37 financial phrases were predicted as legal and 27 legal phrases were predicted as financial.

At the existing 80% confidence cutoff, the current model accepted 63.2% of phrases and was correct on 73.8% of those accepted phrases. The weighted model accepted 62.5% and was correct on 73.5% of those. The probabilities have not been calibrated, so this does not mean “80% confidence” corresponds to an 80% chance of correctness.

## How it was measured

- Rebuilt examples directly from the 24 source survey rows, assigning anonymous contributor IDs from row position. The script reads only the language and phrase-answer columns; it does not load the name or timestamp columns.
- Kept every contributor’s phrases in one fold. Contributors sharing an identical phrase were grouped together too, preventing exact phrase overlap between fold training and evaluation data.
- Stratified folds by both language and intent category. Each fold holds out contributors from both Bemba and Nyanja.
- Recomputed both Logistic Regression variants inside each fold. The frozen encoder and first-token feature extraction match the current training and serving code. The saved production classifier was not changed.
- Evaluated all held-out predictions once, then calculated aggregate and per-language metrics.

The source survey reproduces 416 of the 424 rows currently in `train.csv`. **Eight rows do not have a matching source contributor**, so they were excluded from both training and evaluation in every fold. They need provenance before they can be included in a speaker-held-out evaluation.

## Limits

Only 24 contributors are represented, so these estimates are preliminary and may change substantially with more speakers or dialect coverage. Phrase-level counts do not mean there are hundreds of independent speakers. This experiment measures intent classification only. It does not evaluate semantic translation, urgency scoring, confidence calibration, or safety in medical or legal use.

## Reproduce

From the `ai` directory, run:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ./venv/bin/python evaluate_grouped.py
```

The script writes aggregate metrics to `grouped_cv_report.json`; it does not write message text, names, predictions tied to individual contributors, or embeddings.

To create a private review sheet from the baseline model's held-out errors, run:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ./venv/bin/python evaluate_grouped.py --export-review-sheet
```

This writes up to 10 errors per language and survey label to `/tmp/bantu-sense-review/review_blind.csv`, with blank fields for a fluent reviewer to check language, intent, naturalness, and ambiguity. The matching labels and model predictions go to the separate `review_answer_key.csv`. Give reviewers only the blind sheet and withhold the key until they have finished. Both files are restricted to the current local user and stay outside the repository. Phrase text is copied verbatim and could contain personal information, so share the sheet only if the contributors' consent covers this review; contributor names and timestamps are not included.
