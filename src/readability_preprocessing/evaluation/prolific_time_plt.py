import matplotlib.pyplot as plt
import pandas as pd

from readability_preprocessing.evaluation.utils import DEMOGRAPHIC_DATA_DIR, \
    load_csv_files

# Load the CSV file into a DataFrame
folder_path = DEMOGRAPHIC_DATA_DIR
file_paths = []
for file_path in folder_path.iterdir():
    if file_path.suffix == '.csv':
        file_paths.append(file_path)
df = load_csv_files(file_paths)

# Remove all non-completed surveys
not_completed_codes = ['TIMED-OUT', 'RETURNED']
df = df[~df['Status'].isin(not_completed_codes)]

# Remove all surveys with a "NOCODE" Completion code
df = df[df['Completion code'] != 'NOCODE']

# Get the time taken to complete the survey
time_taken = pd.to_timedelta(df['Time taken'], unit="s").dropna()

# Calculate and display mean, std, and median
mean_time = time_taken.mean().total_seconds()
std_time = time_taken.std().total_seconds()
median_time = time_taken.median().total_seconds()

# Print as "mm:ss"
print(f"Mean time: {mean_time // 60:.0f}:{mean_time % 60:.0f}")
print(f"Std time: {std_time // 60:.0f}:{std_time % 60:.0f}")
print(f"Median time: {median_time // 60:.0f}:{median_time % 60:.0f}")

# Print as seconds
print(f"Mean time: {mean_time:.0f} seconds")
print(f"Std time: {std_time:.0f} seconds")
print(f"Median time: {median_time:.0f} seconds")
print(f"Mean - 1 std: {mean_time - std_time:.0f} seconds")

# Plotting a historgram
# plt.hist(time_taken.dt.total_seconds() // 60, bins=30)
# plt.xlabel('Time taken (minutes)')
# plt.ylabel('Number of participants')
# plt.title('Time taken to complete the survey')
#
# # Mean, median, mean - 1 std
# plt.axvline(mean_time // 60, color='orange', linestyle='dashed', linewidth=2)
# # plt.axvline((mean_time - std_time) // 60, color='red', linestyle='dashed', linewidth=2)
#
# # legend
# plt.legend(['Mean'])
#
# plt.show()

# Plot a box plot (orange line = median)
time_in_seconds = time_taken.dt.total_seconds()
plt.figure(figsize=(6, 8))
plt.boxplot(time_in_seconds)
plt.xticks([1], ['Overall'])
plt.ylabel('Time (minutes)')
plt.title('Time required to complete the survey')

# Update y-axis labels to be in minutes and seconds in 5-minute intervals
plt.yticks(
    [i * 300 for i in range(int(max(time_in_seconds) // 300) + 1)],
    [f"{i // 60:.0f}:{i % 60:.0f}" for i in range(0, int(max(time_in_seconds)) + 1, 300)]
)

plt.show()
