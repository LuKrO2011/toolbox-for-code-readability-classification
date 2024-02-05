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

# # Plot the boxplot
# plt.figure(figsize=(10, 6))
# boxplot = plt.boxplot(time_taken, vert=False, patch_artist=True)
#
# # Customize the boxplot
# plt.title('Time Taken to Complete Survey')
# plt.xlabel('Time (mm:ss)')
# plt.yticks([])  # Hide y-axis ticks

# Calculate and display mean, std, and median
mean_time = time_taken.mean()
std_time = time_taken.std()
median_time = time_taken.median()

print(f"Mean Time: {str(mean_time).split()[-1]}")
print(f"Standard Deviation: {str(std_time).split()[-1]}")
print(f"Median Time: {str(median_time).split()[-1]}")

# Show the plot
plt.show()
