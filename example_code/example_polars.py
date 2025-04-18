import numpy as np
import polars as pl

# Example data
features = [
    np.random.rand(10),  # Example NumPy array for features
    np.random.rand(10),
    np.random.rand(10)
]
labels = [0, 1, 0]  # Example labels
match_ids = ['001', '002', '003']

# Flatten features into separate columns
flattened_features = [list(arr) for arr in features]  # Convert NumPy arrays to lists
column_names = [f"feature_{i}" for i in range(len(flattened_features[0]))]

# Prepare data for Polars DataFrame
data = {col: [row[i] for row in flattened_features] for i, col in enumerate(column_names)}
data["labels"] = labels
data["match_id"] = match_ids

# Create a Polars DataFrame
df = pl.DataFrame(data)

# Output to csv
df.write_csv("polars_test.csv")

# Display the DataFrame
print(df)
