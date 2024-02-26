import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches


from readability_preprocessing.evaluation.utils import DEMOGRAPHIC_DATA_DIR, \
    load_csv_files

PILOT_TIMES = ['7:35', '18:00', '14:00', '13:50', '10:50', '13:04', '9:50', '12:30',
               '12:00', '15:00']

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
pilot_times = np.array(
    [int(time.split(':')[0]) * 60 + int(time.split(':')[1]) for time in PILOT_TIMES])

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
plt.hist(time_taken.dt.total_seconds() // 60, bins=30)
plt.xlabel('Time taken (minutes)')
plt.ylabel('Number of participants')
plt.title('Time taken to complete the survey')

# Mean, median, mean - 1 std
plt.axvline(mean_time // 60, color='orange', linestyle='dashed', linewidth=2)
# plt.axvline((mean_time - std_time) // 60, color='red', linestyle='dashed', linewidth=2)

# legend
plt.legend(['Mean'])

plt.show()

# Plot a box plot (orange line = median)
time_in_seconds = time_taken.dt.total_seconds()
# plt.figure(figsize=(6, 8))
plt.boxplot([pilot_times, time_in_seconds], medianprops=dict(color='orange'))
plt.xticks([1, 2], ["Pilot survey", "Prolific survey"])
plt.ylabel('Time (minutes)')
median_legend = mpatches.Patch(color='orange', label='Median')
plt.legend(handles=[median_legend])
# plt.title('Time required to complete the survey')

# Update y-axis labels to be in minutes and seconds in 5-minute intervals
plt.yticks(
    [i * 300 for i in range(int(max(time_in_seconds) // 300) + 1)],
    [f"{i // 60:.0f}:{i % 60:.0f}" for i in
     range(0, int(max(time_in_seconds)) + 1, 300)]
)

plt.show()
