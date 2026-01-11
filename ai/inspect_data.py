import pandas as pd

# Load the file you downloaded
df = pd.read_csv('raw_data.csv')

# This prints every column name with its number (Index)
for i, col in enumerate(df.columns):
    print(f"Index {i}: {col}")
