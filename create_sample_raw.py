import pandas as pd

# Load the large dataset
df = pd.read_csv("data/raw/swiggy.csv")

# Take a small random sample (e.g., 1%)
sample_df = df.sample(frac=0.01, random_state=42)

# Save it
sample_df.to_csv("data/raw/swiggy_sample.csv", index=False)
print(sample_df.shape)