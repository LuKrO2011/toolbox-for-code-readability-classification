import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.font_utils import (
    get_percentage_formatter,
    set_custom_font,
)
from readability_preprocessing.evaluation.utils import (
    NONE_DIFF_RESULTS_DIR,
    load_json_file,
)

set_custom_font()


def generate_bar_chart(data: list) -> None:
    """
    Generates a bar chart for the relative frequency of 'not_different' cases overall,
    for each stratum, and for each stratum and rdh.
    :param data: The data containing the relative frequency of 'not_different' cases
    :param headline: The headline of the bar chart
    """
    # Extract relevant data for plotting
    strata_labels = [entry["stratum"] for entry in data]
    not_different = [entry["not_different_rel"] for entry in data]

    # Reduce the figure size
    plt.subplots(figsize=(6, 2))

    # Convert not_different to percentages
    not_different = [x * 100 for x in not_different]

    # Create a bar chart for 'different' cases
    plt.bar(strata_labels, not_different)

    # Adding labels, title, and legend
    plt.ylabel("Frequency in %")

    # Display the percentage values on top of the bars with smaller font size
    for i, v in enumerate(not_different):
        plt.text(i, v + 0.5, f"{v:.1f}%", ha="center")  # fontweight="bold"

    # Fix the y-scale to be between 0 and 1
    plt.ylim(0, 30)

    # plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # plt.subplots_adjust(bottom=0.2)  # Increase space at the bottom

    # Set the y-axis to display percentages
    plt.gca().yaxis.set_major_formatter(get_percentage_formatter())
    plt.yticks(range(0, 31, 10))

    # Show the plot
    plt.savefig(
        "sampling_not_different_overall_ylim.pdf", format="pdf", bbox_inches="tight"
    )
    plt.show()


diff_dir = NONE_DIFF_RESULTS_DIR / "statistics.json"
diff_data = load_json_file(diff_dir)

# Replace "stratum0" with "Stratum 0" for better readability
for entry in diff_data[1:]:
    entry["stratum"] = entry["stratum"].replace("stratum", "Stratum ")

# Replace "overall" with "All"
diff_data[0]["stratum"] = "All"

generate_bar_chart(diff_data)

# for stratum in diff_data[1:]:
#     generate_bar_chart(
#         stratum["sub_statistics"],
#         headline=f'Relative Frequency of "Not Different" Cases for '
#                  f'{stratum["stratum"]}',
#     )
