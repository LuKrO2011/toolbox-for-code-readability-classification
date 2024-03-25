import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import set_custom_font
from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_time

set_custom_font()

snippets = load_combined()

java_knowledge_question_id = 16
tuples = question_time(snippets, java_knowledge_question_id)

# Remove all tuples with to large time taken
max_time = 40 * 60
tuples = [t for t in tuples if t[1] < max_time]

# Convert to dictionary
data = {0: [], 1: [], 2: [], 3: [], 4: []}
for t in tuples:
    data[t[0]].append(t[1])

# # Convert the time to minutes
# for key in data.keys():
#     data[key] = [t / 60 for t in data[key]]

# 0 with Expert, 1 with Advanced, 2 with Intermediate, 3 with Beginner, 4 with Novice
data["Expert (5)"] = data.pop(0)
data["Advanced (4)"] = data.pop(1)
data["Intermediate (3)"] = data.pop(2)
data["Beginner (2)"] = data.pop(3)
data["Novice (1)"] = data.pop(4)

# Invert the order
data = dict(reversed(list(data.items())))

# Plot as boxplot
plt.subplots(figsize=(8, 3))
plt.boxplot(data.values(), medianprops={"color": "orange"})
plt.xticks(range(1, len(data.keys()) + 1), data.keys())
plt.ylabel("Time (minutes)")

# Add median to legend
median_legend = mpatches.Patch(color="orange", label="Median")
plt.legend(handles=[median_legend])

# Update y-axis labels to be in minutes and seconds in 5-minute intervals
time_in_seconds = [item for sublist in data.values() for item in sublist]
plt.yticks(
    [i * 300 for i in range(int(max(time_in_seconds) // 300) + 1)],
    [f" {i // 60:.0f}" for i in range(0, int(max(time_in_seconds)) + 1, 300)],
)

plt.savefig("java_knowledge_time.pdf", format="pdf", bbox_inches="tight")
plt.show()
