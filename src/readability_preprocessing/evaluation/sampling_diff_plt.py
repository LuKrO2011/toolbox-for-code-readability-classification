import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import set_custom_font
from readability_preprocessing.evaluation.utils import (
    NONE_DIFF_RESULTS_DIR,
    load_json_file,
)

set_custom_font()


def generate_bar_chart(
    data: list, headline: str = 'Relative Frequency of "Not Different" Cases'
) -> None:
    """
    Generates a bar chart for the relative frequency of 'not_different' cases overall,
    for each stratum, and for each stratum and rdh.
    :param data: The data containing the relative frequency of 'not_different' cases
    :param headline: The headline of the bar chart
    """
    # Extract relevant data for plotting
    strata_labels = [entry["stratum"] for entry in data]
    not_different = [entry["not_different_rel"] for entry in data]

    # Create a bar chart for 'different' cases
    # fig, ax = plt.subplots(figsize=(10, 8))  # Increase the height of the plot
    plt.bar(strata_labels, not_different, color="lightcoral", edgecolor="black")

    # Adding labels, title, and legend
    # plt.xlabel('Stratum (and RDH)')
    plt.ylabel("Relative Frequency")
    # plt.title(headline)

    # Display the percentage values on top of the bars with smaller font size
    for i, v in enumerate(not_different):
        plt.text(
            i,
            v,
            f"{v:.1%}",
            ha="center",
            va="bottom",
            color="black",
            fontweight="bold",
        )

    # Fix the y-scale to be between 0 and 1
    plt.ylim(0, 1)

    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # plt.subplots_adjust(bottom=0.2)  # Increase space at the bottom

    # Show the plot
    plt.tight_layout()
    plt.show()


diff_dir = NONE_DIFF_RESULTS_DIR / "statistics.json"
diff_data = load_json_file(diff_dir)

# Replace "stratum0" with "Stratum 0" for better readability
for entry in diff_data[1:]:
    entry["stratum"] = entry["stratum"].replace("stratum", "Stratum ")

# Replace "overall" with "All"
diff_data[0]["stratum"] = "All"

generate_bar_chart(
    diff_data, headline='Relative Frequency of "Not Different" Cases Overall'
)
# for stratum in diff_data[1:]:
#     generate_bar_chart(
#         stratum["sub_statistics"],
#         headline=f'Relative Frequency of "Not Different" Cases for '
#                  f'{stratum["stratum"]}',
#     )
