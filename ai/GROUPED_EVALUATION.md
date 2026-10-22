# Bantu-Sense intent evaluation

**Run date:** 2026-10-22

**Evaluation:** 5-fold grouped cross-validation by survey contributor
**Detailed aggregate output:** [`grouped_cv_report.json`](grouped_cv_report.json)

## Result

The current frozen Afro-XLM-R large encoder plus Logistic Regression head reached **63.2% accuracy** on 416 source-traceable phrases from contributors held out of the corresponding training fold. The majority-class baseline is **35.1%**.

| Measure | Result |
| --- | ---: |
| Overall accuracy | 63.2% |
| Overall macro F1 | 63.2% |
| Bemba accuracy | 68.6% |
| Nyanja accuracy | 58.6% |
| Legal recall, both languages | 59.8% |
| Legal recall, Nyanja | 55.2% |

The model is showing a useful signal above the simple baseline, but it still makes substantial errors. Legal intent is its weakest category, particularly for Nyanja. In the confusion matrix, 37 financial phrases were predicted as legal, while 27 legal phrases were predicted as financial.

At the existing 80% confidence cutoff, the fold models accepted 63.2% of phrases and were correct on 73.8% of those accepted phrases; 153 of 416 were below the cutoff. The probabilities have not been calibrated, so this is a description of the current threshold behavior, not evidence that “80% confidence” means an 80% chance of correctness.

## How it was measured

- Rebuilt examples directly from the 24 source survey rows, assigning anonymous contributor IDs from row position. The script reads only the language and phrase-answer columns; it does not load the name or timestamp columns.
- Kept every contributor’s phrases in one fold. Contributors sharing an identical phrase were grouped together too, preventing exact phrase overlap between fold training and evaluation data.
- Stratified folds by both language and intent category. Each fold holds out contributors from both Bemba and Nyanja.
- Recomputed the Logistic Regression classifier inside each fold. The frozen encoder and first-token feature extraction match the current training and serving code. The saved production classifier was not changed.
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
