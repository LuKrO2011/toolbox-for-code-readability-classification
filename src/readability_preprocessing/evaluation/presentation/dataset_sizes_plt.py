import matplotlib.pyplot as plt
import numpy as np

# Get a colormap (pastel1)
cmap = plt.get_cmap('Set3')

# Define the numbers and their colors
numbers = [100, 120, 200]
colors = [cmap(0), cmap(1), cmap(2)]
legend_labels = ['B&W', 'Dorn', 'Scalabrino']

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(4, 1))
bars = []
for i in range(len(numbers)):
    bar = ax.barh(0, numbers[i], color=colors[i], left=np.sum(numbers[:i]))
    bars.append(bar)
    ax.text(np.sum(numbers[:i]) + numbers[i] / 2, 0, legend_labels[i], ha='center', va='center', color='black')

# Set labels and limits
ax.set_yticks([])
ax.set_xlim(0, np.sum(numbers))
ax.set_xticks([])
# ax.set_xlabel('Number of code snippets')
# ax.set_xticks(np.arange(0, np.sum(numbers) + 1, 60))

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig('dataset_sizes_1.png', dpi=1000)
plt.show()

numbers.append(69000)
colors.append(cmap(3))
legend_labels.append('Mined & Modified dataset')

# Create a horizontal bar chart
fig, ax = plt.subplots(figsize=(4, 1))
bars = []
for i in range(len(numbers)):
    bar = ax.barh(0, numbers[i], color=colors[i], left=np.sum(numbers[:i]))
    bars.append(bar)

# Add label for the last bar
i = 3
ax.text(np.sum(numbers[:i]) + numbers[i] / 2, 0, legend_labels[i], ha='center', va='center', color='black')

# Set labels and limits
ax.set_yticks([])
ax.set_xlim(0, np.sum(numbers))
ax.set_xticks([])
# ax.set_xlabel('Number of code snippets')
# ax.set_xticks(np.arange(0, np.sum(numbers) + 1, 69000 / 1))

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig('dataset_sizes_2.png', dpi=1000)
plt.show()
