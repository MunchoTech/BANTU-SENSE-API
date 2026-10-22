# Bantu-Sense analysis response contract

Both `POST /analyze` (Python AI service) and `POST /api/inquiries/send` (Spring Boot API) return the same JSON analysis shape. The Spring Boot endpoint persists the inquiry before returning the analysis.

## Request bodies

Python service:

```json
{
  "text": "Mwana wanga akudwala kwambiri, ndithandizeni.",
  "donateForReview": false
}
```

Spring Boot API:

```json
{
  "originalText": "Mwana wanga akudwala kwambiri, ndithandizeni.",
  "donateForReview": false
}
```

`donateForReview` is optional and defaults to `false`. It only permits an uncertain message to be added to the configured human-review log; it does not change ordinary inquiry persistence in Spring Boot.

## Response fields

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | string | `analyzed`, `uncertain`, or `unavailable`. |
| `intent` | string | Predicted class (`MEDICAL`, `LEGAL`, `FINANCIAL`) or `UNCERTAIN`. |
| `confidence` | number or `null` | Classifier confidence as a percentage from 0 to 100. |
| `urgencyScore` | integer or `null` | Behavioral urgency score from 1 to 10. `null` when analysis is unavailable. |
| `urgencyLevel` | string | `ROUTINE`, `HIGH`, `CRITICAL`, or `UNKNOWN` when unavailable. |
| `reviewSubmitted` | boolean | Whether an uncertain message was saved to the review log. Always present. |
| `message` | string | Human-readable result or service state. |
| `semanticContext` | string or `null` | Short context summary when analysis is available. |

Successful or uncertain analysis returns HTTP `200`. If the Python service is unavailable, Spring returns HTTP `503` with the same fields and `status: "unavailable"`.

## Example: analyzed

```json
{
  "status": "analyzed",
  "intent": "MEDICAL",
  "confidence": 87.42,
  "urgencyScore": 9,
  "urgencyLevel": "CRITICAL",
  "reviewSubmitted": false,
  "message": "Your message has been analyzed.",
  "semanticContext": "Request identified as medical with critical priority."
}
```

## Example: uncertain

```json
{
  "status": "uncertain",
  "intent": "UNCERTAIN",
  "confidence": 55.0,
  "urgencyScore": 5,
  "urgencyLevel": "ROUTINE",
  "reviewSubmitted": false,
  "message": "The analysis was uncertain. Your message was not stored for model improvement.",
  "semanticContext": null
}
```

The field names and value types are shared across the Python service, Spring Boot response, and demo UI. Keep this document updated when the response contract changes.
