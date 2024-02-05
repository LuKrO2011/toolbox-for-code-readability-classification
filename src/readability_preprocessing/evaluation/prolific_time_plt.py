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

# Calculate and display mean, std, and median
mean_time = time_taken.mean().total_seconds()
std_time = time_taken.std().total_seconds()
median_time = time_taken.median().total_seconds()

# Print as "mm:ss"
print(f"Mean time: {mean_time // 60:.0f}:{mean_time % 60:.0f}")
print(f"Std time: {std_time // 60:.0f}:{std_time % 60:.0f}")
print(f"Median time: {median_time // 60:.0f}:{median_time % 60:.0f}")

# Plotting
time_in_seconds = time_taken.dt.total_seconds()
plt.figure(figsize=(6, 8))
plt.boxplot(time_in_seconds)
plt.xticks([1], ['Overall'])
plt.ylabel('Time (minutes)')
plt.title('Time required to complete the survey')

# Update y-axis labels
plt.yticks(plt.yticks()[0],
           ['{}:{:02d}'.format(int(seconds // 60), int(seconds % 60)) for seconds in
            plt.yticks()[0]])
plt.show()
