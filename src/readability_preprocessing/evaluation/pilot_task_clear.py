import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import set_custom_font

set_custom_font()

ratings = {"1": 1, "2": 1, "3": 0, "4": 5, "5": 3}


def generate_bar_chart(data):
    keys = list(data.keys())
    values = list(data.values())

    plt.subplots(figsize=(3, 3))
    plt.bar(keys, values)
    plt.xlabel("Level of clarity")
    plt.ylabel("Number of ratings")
    plt.savefig("pilot_survey_task_clearness.pdf", format="pdf", bbox_inches="tight")
    plt.show()


generate_bar_chart(ratings)
