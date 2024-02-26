import matplotlib.pyplot as plt
import numpy as np

times_list = ['7:35', '18:00', '14:00', '13:50', '10:50', '13:04', '9:50', '12:30', '12:00', '15:00']

# Convert times to minutes
time_in_minutes = np.array([int(time.split(':')[0])*60 + int(time.split(':')[1]) for time in times_list])

# Plotting
plt.figure(figsize=(6, 8))
plt.boxplot(time_in_minutes)
plt.xticks([1], ["Overall"])
plt.ylabel('Time (minutes)')

# Update y-axis labels
plt.yticks(plt.yticks()[0], ['{}:{:02d}'.format(int(minutes // 60), int(minutes % 60)) for minutes in plt.yticks()[0]])

# Convert time values to hours for statistics calculation
time_in_hours = time_in_minutes / 60

# Calculate and print statistics
average_time = np.mean(time_in_hours)
median_time = np.median(time_in_hours)
std_deviation = np.std(time_in_hours)

print("Statistics:")
print("Average: {:.2f} minutes".format(average_time))
print("Median: {:.2f} minutes".format(median_time))
print("Standard Deviation: {:.2f} minutes".format(std_deviation))

# Show the plot
plt.show()
