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
time_in_seconds = df['Time taken']
time_in_minutes = time_in_seconds / 60

# Plotting
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

# Calculate and print statistics
average_time = time_in_minutes.mean()
median_time = time_in_minutes.median()
std_deviation = time_in_minutes.std()

# Print time values as mm:ss
print("Statistics:")
print("Average: {:.2f} minutes".format(average_time))
print("Median: {:.2f} minutes".format(median_time))
print("Standard Deviation: {:.2f} minutes".format(std_deviation))
