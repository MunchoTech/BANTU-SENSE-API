import joblib
from transformers import pipeline

# 1. LOAD THE TOOLS
print("Loading the Brain and the trained Mouth...")
extractor = pipeline("feature-extraction", model="Davlan/afro-xlmr-large-76L")
clf = joblib.load('bantu_sense_head.joblib')

def analyze_sense(text):
    # Turn the text into math (the Brain)
    feat = extractor(text[:512])[0][0]
    
    # Predict the label (the Mouth)
    label = clf.predict([feat])[0]
    
    # Get the confidence score
    probs = clf.predict_proba([feat])[0]
    confidence = max(probs) * 100
    
    return label, confidence

# 2. TEST PHRASES
test_phrases = [
    "Nili ndi malungo kwambiri",         # Medical?
    "Nifuna kuchotsa ndalama ku bank",   # Financial?
    "Neighbor wanga akunofuna kunimenya" # Legal?
]

print("\n--- Bantu-Sense Real-World Test ---")
for phrase in test_phrases:
    intent, score = analyze_sense(phrase)
    print(f"Phrase: {phrase}")
    print(f"Detected Intent: {intent.upper()}")
    print(f"Confidence: {score:.2f}%\n")
