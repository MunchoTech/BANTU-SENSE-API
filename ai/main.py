from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from transformers import pipeline
import csv
from datetime import datetime

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
        return "CRITICAL (9/10)"
    elif score == 9:
        return "HIGH (9/10)"
    return f"ROUTINE ({score}/10)"

# --- 2. THE BRAIN LOADING ---
print("Waking up Bantu-Sense...")
extractor = pipeline("feature-extraction", model="Davlan/afro-xlmr-large-76L")
clf = joblib.load('bantu_sense_head.joblib')

class UserInput(BaseModel):
    text: str

@app.post("/analyze")
async def predict_intent(data: UserInput):
    user_text = data.text
    feat = extractor(user_text[:512])[0][0]
    
    intent_label = clf.predict([feat])[0]
    probs = clf.predict_proba([feat])[0]
    confidence = max(probs) * 100

    # --- 3. APPLYING BEHAVIORAL LOGIC ---
    urgency_status = calculate_urgency(user_text, intent_label.upper())

    # --- 4. THE AUDIT LOG (Lusaka Protocol) ---
    if confidence < 80.0:
        with open('audit_log.csv', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), user_text, intent_label, f"{confidence:.2f}%"])
        
        return {
            "status": "uncertain",
            "intent": "UNCERTAIN",
            "urgency": urgency_status,
            "confidence": f"{confidence:.2f}%",
            "message": "Logged to Lusaka Protocol for refinement."
        }

    # --- 5. THE WINNING RESPONSE ---
    return {
        "status": "success",
        "intent": intent_label.upper(),
        "urgency_score": urgency_status,
        "confidence": f"{confidence:.2f}%",
        "semantic_context": f"Request identified as {intent_label.lower()} with {urgency_status.split()[0].lower()} priority."
    }
