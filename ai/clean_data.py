import pandas as pd
import re

df = pd.read_csv('raw_data.csv')
final_data = []

for col in df.columns:
    if "medical" in col.lower() or "health" in col.lower():
        label = "medical"
    elif "finance" in col.lower() or "money" in col.lower():
        label = "financial"
    elif "legal" in col.lower() or "rights" in col.lower():
        label = "legal"
    else:
        continue

    for block in df[col]:
        if pd.notna(block):
            # 1. SPLIT: This splits the block into a list of lines using the 'Enter' key (\n)
            # or if people used numbers like 1. 2. 
            lines = re.split(r'\n|\d+\.', str(block))
            
            for line in lines:
                clean_line = line.strip() # Remove extra spaces
                # 2. FILTER: Only add if the line isn't empty and has more than 3 characters
                if len(clean_line) > 3:
                    final_data.append({"text": clean_line, "label": label})

clean_df = pd.DataFrame(final_data)
clean_df.to_csv('train.csv', index=False)
print(f"Success! You now have {len(clean_df)} clean individual phrases in train.csv.")
