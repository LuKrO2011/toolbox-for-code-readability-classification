import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter

from readability_preprocessing.evaluation.utils import DATASET_SIZES_CSV, load_csv_file

# TODO: Set font

# Load CSV into a DataFrame
ds_sizes = load_csv_file(DATASET_SIZES_CSV)

# Convert 'Publication date' column to datetime format
ds_sizes["Publication date"] = pd.to_datetime(
    ds_sizes["Publication date"], errors="coerce"
)

# Filter data for dates after 1992
ds_sizes = ds_sizes[ds_sizes["Publication date"].dt.year >= 2000]

# Sort DataFrame by 'Publication date'
ds_sizes = ds_sizes.sort_values(by="Publication date")

# Plotting with log scale on y-axis
plt.figure(figsize=(4, 3))
plt.scatter(
    ds_sizes["Publication date"],
    ds_sizes["Training dataset size (datapoints)"],
    label="Data Points",
)

# Add a trend line
ds_sizes_cleaned = ds_sizes.dropna(
    subset=["Publication date", "Training dataset size (datapoints)"]
)

z = np.polyfit(
    pd.to_numeric(ds_sizes_cleaned["Publication date"]),
    np.log(ds_sizes_cleaned["Training dataset size (datapoints)"]),
    1,
)

p = np.poly1d(z)
trend_line_dates = pd.date_range(
    ds_sizes["Publication date"].min(), ds_sizes["Publication date"].max(), freq="M"
)
plt.plot(
    trend_line_dates,
    np.exp(p(pd.to_numeric(trend_line_dates))),
    "r--",
    label="Trend Line",
)

# Merged
merged_date = pd.to_datetime("2024-01-01")
merged_value = 421
plt.scatter(
    merged_date,
    merged_value,
    color="green",
    marker="*",
    s=200,
    label="All Readability Datasets Combined",
)

# With comments
merged_date = pd.to_datetime("2024-01-01")
merged_value = 69276
plt.scatter(
    merged_date,
    merged_value,
    color="orange",
    marker="*",
    s=200,
    label="All Readability Datasets Combined (2012)",
)

# Without comments
# merged_date = pd.to_datetime("2024-01-01")
# merged_value = 700000
# plt.scatter(
#     merged_date,
#     merged_value,
#     color="orange",
#     marker="*",
#     s=200,
#     label="All Readability Datasets Combined (2012)",
# )

plt.xlabel("Publication Date")
plt.ylabel("Dataset Size")
plt.yscale("log")
plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))  # Format x-axis as dates
plt.xticks(["2000-01-01", "2012-01-01", "2024-01-01"])

plt.tight_layout()

# Show the plot
plt.savefig("dataset_sizes.png", dpi=1000)
plt.show()
