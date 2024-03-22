import matplotlib.pyplot as plt

from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_rating_std

snippets = load_combined()

java_knowledge_question_id = 16
group_diffs = question_rating_std(snippets, java_knowledge_question_id)

# 0 = Expert, 1 = Advanced, 2 = Intermediate, 3 = Beginner, 4 = Novice
group_diffs = {"Expert": group_diffs[0], "Advanced": group_diffs[1], "Intermediate": group_diffs[2],
               "Beginner": group_diffs[3], "Novice": group_diffs[4]}

plt.bar(group_diffs.keys(), group_diffs.values())
plt.ylabel("Normalized deviation from average rating")
plt.show()
