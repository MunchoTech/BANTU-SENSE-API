from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field
import joblib
from transformers import pipeline
import csv
from datetime import datetime
import os
from pathlib import Path

app = FastAPI()

# --- 1. THE LOGIC LAYER (Your new function) ---
def calculate_urgency(text, intent):
    score = 5  # Neutral/Default
    # 'high_intensity_words' act as Behavioral Markers
    high_intensity_words = ['fwa', 'mwazi', 'menya', 'paya', 'vutitsa', 'emergency', 'help']
    
    if any(word in text.lower() for word in high_intensity_words):
        score = 9
    
    # Context-specific logic: Medical + High Score = Critical
    if intent == "MEDICAL" and score == 9:
        level = "CRITICAL"
    elif score == 9:
        level = "HIGH"
    else:
        level = "ROUTINE"
    return score, level

# --- 2. THE BRAIN LOADING ---
print("Waking up Bantu-Sense...")
extractor = pipeline("feature-extraction", model="Davlan/afro-xlmr-large-76L")
clf = joblib.load('bantu_sense_head.joblib')

class UserInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    text: str
    donate_for_review: bool = Field(
        default=False,
        alias="donateForReview",
        description="Explicitly allow this message to be stored for human review and model improvement.",
    )


def save_review_candidate(text: str, intent: str, confidence: float) -> bool:
    """Save a low-confidence message only after opt-in and explicit storage configuration."""
    review_log_path = os.environ.get("BANTU_REVIEW_LOG_PATH")
    if not review_log_path:
        return False

    path = Path(review_log_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="a", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([datetime.now().isoformat(), text, intent, f"{confidence:.2f}%"])
    return True

@app.post("/analyze")
async def predict_intent(data: UserInput):
    user_text = data.text
    feat = extractor(user_text[:512])[0][0]
    
    intent_label = clf.predict([feat])[0]
    probs = clf.predict_proba([feat])[0]
    confidence = max(probs) * 100

    # --- 3. APPLYING BEHAVIORAL LOGIC ---
    urgency_score, urgency_level = calculate_urgency(user_text, intent_label.upper())

    # --- 4. OPTIONAL, CONSENT-BASED REVIEW COLLECTION ---
    if confidence < 80.0:
        review_submitted = data.donate_for_review and save_review_candidate(
            user_text, intent_label, confidence
        )
        return {
            "status": "uncertain",
            "intent": "UNCERTAIN",
            "confidence": round(confidence, 2),
            "urgencyScore": urgency_score,
            "urgencyLevel": urgency_level,
            "reviewSubmitted": review_submitted,
            "message": (
                "Your message was submitted for review with your consent."
                if review_submitted
                else "The analysis was uncertain. Your message was not stored for model improvement."
            ),
            "semanticContext": None,
        }

    # --- 5. THE WINNING RESPONSE ---
    return {
        "status": "analyzed",
        "intent": intent_label.upper(),
        "confidence": round(confidence, 2),
        "urgencyScore": urgency_score,
        "urgencyLevel": urgency_level,
        "reviewSubmitted": False,
        "message": "Your message has been analyzed.",
        "semanticContext": f"Request identified as {intent_label.lower()} with {urgency_level.lower()} priority.",
    }
