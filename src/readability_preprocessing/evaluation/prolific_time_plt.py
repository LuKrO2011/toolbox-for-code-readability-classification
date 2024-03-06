import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from readability_preprocessing.evaluation.font_utils import set_custom_font
from readability_preprocessing.evaluation.utils import (
    DEMOGRAPHIC_DATA_DIR,
    load_csv_files,
)

set_custom_font()

PILOT_TIMES = [
    "7:35",
    "18:00",
    "14:00",
    "13:50",
    "10:50",
    "13:04",
    "9:50",
    "12:30",
    "12:00",
    "15:00",
]

# Load the CSV file into a DataFrame
folder_path = DEMOGRAPHIC_DATA_DIR
file_paths = []
for file_path in folder_path.iterdir():
    if file_path.suffix == ".csv":
        file_paths.append(file_path)
survey_data = load_csv_files(file_paths)

# Remove all non-completed surveys
not_completed_codes = ["TIMED-OUT", "RETURNED"]
survey_data = survey_data[~survey_data["Status"].isin(not_completed_codes)]

# Remove all surveys with a "NOCODE" Completion code
survey_data = survey_data[survey_data["Completion code"] != "NOCODE"]

# Get the time taken to complete the survey
time_taken = pd.to_timedelta(survey_data["Time taken"], unit="s").dropna()
pilot_times = np.array(
    [int(time.split(":")[0]) * 60 + int(time.split(":")[1]) for time in PILOT_TIMES]
)

# Calculate and display mean, std, and median
mean_time = time_taken.mean().total_seconds()
std_time = time_taken.std().total_seconds()
median_time = time_taken.median().total_seconds()
min_time = time_taken.min().total_seconds()
max_time = time_taken.max().total_seconds()

# Print as "mm:ss"
print(f"Mean time: {mean_time // 60:.0f}:{mean_time % 60:.0f}")
print(f"Std time: {std_time // 60:.0f}:{std_time % 60:.0f}")
print(f"Median time: {median_time // 60:.0f}:{median_time % 60:.0f}")
print(f"Min time: {min_time // 60:.0f}:{min_time % 60:.0f}")
print(f"Max time: {max_time // 60:.0f}:{max_time % 60:.0f}")

# Print as seconds
print(f"Mean time: {mean_time:.0f} seconds")
print(f"Std time: {std_time:.0f} seconds")
print(f"Median time: {median_time:.0f} seconds")
print(f"Mean - 1 std: {mean_time - std_time:.0f} seconds")

# Plotting a historgram
plt.subplots(figsize=(5, 3))
plt.hist(time_taken.dt.total_seconds() // 60, bins=30)
plt.xlabel("Time taken (minutes)")
plt.ylabel("Number of participants")

# Mean, median, mean - 1 std
plt.axvline(mean_time // 60, color="orange", linestyle="dashed", linewidth=2)

# legend
plt.legend(["Mean"])

plt.savefig("survey_time_histogramm.pdf", format="pdf", bbox_inches="tight")
plt.show()

# Plot a box plot (orange line = median)
plt.subplots(figsize=(3, 3))
time_in_seconds = time_taken.dt.total_seconds()
plt.boxplot([pilot_times, time_in_seconds], medianprops={"color": "orange"})
plt.xticks([1, 2], ["Pilot survey", "Prolific survey"])
plt.ylabel("Time (minutes)")
median_legend = mpatches.Patch(color="orange", label="Median")
plt.legend(handles=[median_legend])
# plt.title('Time required to complete the survey')

# Update y-axis labels to be in minutes and seconds in 5-minute intervals
plt.yticks(
    [i * 300 for i in range(int(max(time_in_seconds) // 300) + 1)],
    [
        f"{i // 60:.0f}:{i % 60:.0f}"
        for i in range(0, int(max(time_in_seconds)) + 1, 300)
    ],
)

plt.savefig("survey_times.pdf", format="pdf", bbox_inches="tight")
plt.show()
