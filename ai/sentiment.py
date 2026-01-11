# 1. THE TOOLS: Import the 'pipeline' function from the Transformers library.
# Think of 'pipeline' as a high-level manager that handles the complex math for us.
from transformers import pipeline

# 2. THE ENGINE: Tell the code which specific "brain" to use.
# We are using Afro-XLMR because it was trained to respect African languages.
model_name = "Davlan/afro-xlmr-large-76L"

# 3. THE INITIALIZATION: Create the 'classifier' object.
# We tell it two things: 
# - What to do: "zero-shot-classification" (Guessing labels without prior training).
# - Which model to use: The one we defined above.
print(f"Loading {model_name} into memory...")
classifier = pipeline("zero-shot-classification", model=model_name)

# 4. THE LOGIC: Define a function to process our Zambian phrases.
def analyze_zambian_sense(text):
    # These are the "Senses" (categories) we want the AI to choose from.
    candidate_labels = ["positive", "negative", "neutral"]
    
    # This is your "Cultural Interpretability Layer."
    # We provide a Nyanja sentence template to help the AI 'think' in the right language.
    template = "Munthu uyu amvela {}"
    
    # We feed the text, labels, and template into the classifier.
    # The result is a dictionary containing the scores and predicted labels.
    result = classifier(text, candidate_labels, hypothesis_template=template)
    
    return result

# 5. THE TEST: Give the engine something to analyze.
phrase = "Nili bwino"
output = analyze_zambian_sense(phrase)

# 6. THE RESULTS: Print the findings in a clear way.
print(f"\n--- Bantu-Sense Analysis ---")
print(f"Input: {phrase}")
print(f"Top Sense: {output['labels'][0]}")
print(f"Confidence: {round(output['scores'][0] * 100, 2)}%")
