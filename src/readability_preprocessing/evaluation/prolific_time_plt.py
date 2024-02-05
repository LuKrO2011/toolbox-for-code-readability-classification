import matplotlib.pyplot as plt
import pandas as pd

from readability_preprocessing.evaluation.utils import load_csv_file, \
    DEMOGRAPHIC_DATA_DIR

# Load the CSV file into a DataFrame
file_path = DEMOGRAPHIC_DATA_DIR / "p1s0.csv"
df = load_csv_file(file_path)

# Remove all samples which have "TIMED-OUT" as status
df = df[df['Status'] != 'TIMED-OUT']

# Get the time taken to complete the survey
time_taken = pd.to_timedelta(df['Time taken'], unit="s")

# Plot the boxplot
plt.figure(figsize=(10, 6))
boxplot = plt.boxplot(time_taken, vert=False, patch_artist=True)

# Customize the boxplot
plt.title('Time Taken to Complete Survey')
plt.xlabel('Time (mm:ss)')
plt.yticks([])  # Hide y-axis ticks

# Calculate and display mean, std, and median
mean_time = time_taken.mean().total_seconds()
std_time = time_taken.std().total_seconds()
median_time = time_taken.median().total_seconds()

# Print as "mm:ss"
print(f"Mean time: {mean_time // 60:.0f}:{mean_time % 60:.0f}")
print(f"Std time: {std_time // 60:.0f}:{std_time % 60:.0f}")
print(f"Median time: {median_time // 60:.0f}:{median_time % 60:.0f}")

# Show the plot
plt.show()
