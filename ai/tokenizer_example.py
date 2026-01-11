from transformers import AutoTokenizer

# Load Afro-XLM-R
model_name = "Davlan/afro-xlmr-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Test sentence
sentence = "Nili bwino"

# Tokenize
tokens = tokenizer(sentence)
print("Tokens:", tokens)
print("Token IDs:", tokens['input_ids'])

print("hello world")