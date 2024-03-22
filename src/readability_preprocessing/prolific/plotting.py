from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_time

snippets = load_combined()

java_knowledge_question_id = 16
tuples = question_time(snippets, java_knowledge_question_id)

# Remove all tuples where time taken is not a number
tuples = [t for t in tuples if t[1] is not None]

# Remove all tuples where java knowledge is not a number
tuples = [t for t in tuples if t[0] is not None]

# Remove all tuples with to large time taken
max_time = 45 * 60
tuples = [t for t in tuples if t[1] < max_time]

# Plot the data
import matplotlib.pyplot as plt

x = [t[0] for t in tuples]
y = [t[1] for t in tuples]
plt.scatter(x, y)
plt.xlabel("Java Knowledge")
plt.ylabel("Time Required")
plt.show()

# Plot the data as 5 violins (0, 1, 2, 3, 4) java knowledge

data = {0: [], 1: [], 2: [], 3: [], 4: []}
for t in tuples:
    data[t[0]].append(t[1])

plt.violinplot(data.values(), showmeans=True)
plt.xticks(range(1, 6), data.keys())
plt.xlabel("Java Knowledge")
plt.ylabel("Time Required")
plt.show()

# Plot as boxplot
plt.boxplot(data.values())
plt.xticks(range(1, 6), data.keys())
plt.xlabel("Java Knowledge")
plt.ylabel("Time Required")
plt.show()
