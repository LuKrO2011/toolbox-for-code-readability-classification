import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import set_custom_font
from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import question_rating_std_sum

set_custom_font()

snippets = load_combined()

java_knowledge_question_id = 16
group_diffs = question_rating_std_sum(snippets, java_knowledge_question_id)

# 0 = Expert, 1 = Advanced, 2 = Intermediate, 3 = Beginner, 4 = Novice
group_diffs = {
    "Expert (5)": group_diffs[0],
    "Advanced (4)": group_diffs[1],
    "Intermediate (3)": group_diffs[2],
    "Beginner (2)": group_diffs[3],
    "Novice (1)": group_diffs[4],
}

# Invert the order
group_diffs = dict(reversed(list(group_diffs.items())))

plt.subplots(figsize=(8, 3))
plt.bar(group_diffs.keys(), group_diffs.values())
plt.ylabel("Rating deviation")

plt.savefig("java_knowledge_ratings.pdf", format="pdf", bbox_inches="tight")
plt.show()
