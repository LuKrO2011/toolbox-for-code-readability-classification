import matplotlib.pyplot as plt
import numpy as np

# Get a colormap (pastel1)
cmap = plt.get_cmap('Set3')

# Define the numbers and their colors
numbers = [100, 120, 200]
colors = [cmap(0), cmap(1), cmap(2)]

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(4, 1))
for i in range(len(numbers)):
    ax.barh(0, numbers[i], color=colors[i], left=np.sum(numbers[:i]))

# Set labels and limits
ax.set_yticks([])
ax.set_xlim(0, np.sum(numbers))
ax.set_xlabel('Number of code snippets')

# Add legend
legend_labels = ['B&W', 'Dorn', 'Scalabrino']
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i], ec="k") for i in range(len(numbers))]
ax.legend(legend_handles, legend_labels)

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Set x-axis ticks at intervals of 20
ax.set_xticks(np.arange(0, np.sum(numbers) + 1, 60))

plt.tight_layout()
plt.show()

numbers.append(69276)
colors.append(cmap(3))

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(4, 1))
for i in range(len(numbers)):
    ax.barh(0, numbers[i], color=colors[i], left=np.sum(numbers[:i]))

# Set labels and limits
ax.set_yticks([])
ax.set_xlim(0, np.sum(numbers))
ax.set_xlabel('Number of code snippets')

# Add legend
legend_labels = ['B&W', 'Dorn', 'Scalabrino', 'Mined & Modified']  # Update legend labels
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i], ec="k") for i in range(len(numbers))]
ax.legend(legend_handles, legend_labels)

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Set x-axis ticks at intervals of 20000
ax.set_xticks(np.arange(0, np.sum(numbers) + 1, 69000 / 4))

plt.tight_layout()
plt.show()
