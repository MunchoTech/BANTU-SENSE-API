import pandas as pd
from transformers import pipeline
import joblib # Used to save our "Mouth" once it's trained
from sklearn.linear_model import LogisticRegression

# 1. LOAD DATA
df = pd.read_csv('train.csv')

# 2. LOAD THE BRAIN (Feature Extractor)
# We use the same model, but we tell it to just give us the "features" (vectors)
print("Loading Afro-XLMR Brain...")
extractor = pipeline("feature-extraction", model="Davlan/afro-xlmr-large-76L")

# 3. TRANSFORM TEXT TO MATH (Embeddings)
print("Translating Nyanja phrases into math vectors... (This may take a few mins)")
def get_embedding(text):
    # We take the average of the last hidden state to get one vector per sentence
    embeddings = extractor(text[:512]) # Limit text length to 512 characters
    return embeddings[0][0] # Return the core 'meaning' vector

# Create a list of all our math vectors
X = [get_embedding(t) for t in df['text']]
y = df['label'] # Our categories

# 4. TRAIN THE "MOUTH" (Classifier)
print("Training the intent-classifier head...")
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

# 5. SAVE THE RESULT
# We save the "Mouth" so we don't have to train it again
joblib.dump(clf, 'bantu_sense_head.joblib')
print("Success! Your Bantu-Sense Brain now has a trained Mouth.")
