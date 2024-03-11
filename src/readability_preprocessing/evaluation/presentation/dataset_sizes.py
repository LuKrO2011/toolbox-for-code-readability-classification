import matplotlib.pyplot as plt
import pandas as pd

from readability_preprocessing.evaluation.utils import DATASET_SIZES_CSV, load_csv_file

# Load CSV into a DataFrame
ds_sizes = load_csv_file(DATASET_SIZES_CSV)

# Convert 'Publication date' column to datetime format
ds_sizes["Publication date"] = pd.to_datetime(
    ds_sizes["Publication date"], errors="coerce"
)

# Filter data for dates after 1992
ds_sizes = ds_sizes[ds_sizes["Publication date"].dt.year >= 1992]

# Sort DataFrame by 'Publication date'
ds_sizes = ds_sizes.sort_values(by="Publication date")

# Plotting with log scale on y-axis
plt.figure(figsize=(10, 6))
plt.scatter(
    ds_sizes["Publication date"],
    ds_sizes["Training dataset size (datapoints)"],
    label="Data Points",
)
plt.title("Training Dataset Size vs. Publication Date")
plt.xlabel("Publication Date")
plt.ylabel("Training Dataset Size (datapoints)")
plt.yscale("log")  # Use log scale on y-axis
plt.xticks(rotation=45)


plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
