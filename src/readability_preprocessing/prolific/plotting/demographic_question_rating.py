import matplotlib.pyplot as plt

from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_rating_std

snippets = load_combined()

java_knowledge_question_id = 16
tuples = question_rating_std(snippets, java_knowledge_question_id)

# Sum up the values for the second part of the tuple
data = {}
for tuple in tuples:
    if tuple[0] not in data:
        data[tuple[0]] = 0
    data[tuple[0]] += tuple[1]

# Replace 0 with Expert, 1 with Advanced, 2 with Intermediate, 3 with Beginner, 4 with Novice
data["Expert"] = data.pop(0)
data["Advanced"] = data.pop(1)
data["Intermediate"] = data.pop(2)
data["Beginner"] = data.pop(3)
data["Novice"] = data.pop(4)

# Plot as a bar chart
plt.bar(data.keys(), data.values())
plt.xlabel("Java Knowledge")
plt.ylabel("Standard Deviation")
plt.show()
