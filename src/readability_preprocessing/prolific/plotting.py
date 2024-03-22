import matplotlib.pyplot as plt
from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_time

snippets = load_combined()

java_knowledge_question_id = 16
tuples = question_time(snippets, java_knowledge_question_id)

# Remove all tuples with to large time taken
max_time = 45 * 60
tuples = [t for t in tuples if t[1] < max_time]

# Convert to dictionary
data = {0: [], 1: [], 2: [], 3: [], 4: []}
for t in tuples:
    data[t[0]].append(t[1])

# Convert the time to minutes
for key in data.keys():
    data[key] = [t / 60 for t in data[key]]

# Replace 0 with Expert, 1 with Advanced, 2 with Intermediate, 3 with Beginner, 4 with Novice
data["Expert"] = data.pop(0)
data["Advanced"] = data.pop(1)
data["Intermediate"] = data.pop(2)
data["Beginner"] = data.pop(3)
data["Novice"] = data.pop(4)

# Plot as boxplot
plt.boxplot(data.values())
plt.xticks(range(1, len(data.keys()) + 1), data.keys())
plt.ylabel("Time taken (minutes)")

plt.show()
