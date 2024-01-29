import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.utils import NONE_DIFF_RESULTS_DIR, \
    load_json_file


def generate_stacked_bar_chart(data: list) -> None:
    """
    Generates a stacked bar chart.
    :param data: The data to plot
    :return: The plot
    """
    # Extract relevant data for plotting
    strata_labels = [entry["stratum"] for entry in data]
    not_different_rel_values = [entry["not_different_rel"] for entry in data]
    different_rel_values = [entry["different_rel"] for entry in data]

    # Create a stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.8

    # Plotting the bars
    bars1 = plt.bar(strata_labels, not_different_rel_values, color='lightblue',
                    edgecolor='black', width=bar_width, label='Not Different')
    bars2 = plt.bar(strata_labels, different_rel_values,
                    bottom=not_different_rel_values, color='lightcoral',
                    edgecolor='black', width=bar_width, label='Different')

    # Adding labels, title, and legend
    plt.xlabel('Stratum')
    plt.ylabel('Relative Frequency')
    plt.title('Relative Frequency of Different and Not Different Cases in Each Stratum')
    plt.legend()

    # Display the percentage values on top of the bars
    for bar in bars1 + bars2:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2%}', ha='center',
                 va='bottom', color='black', fontweight='bold')

    # Show the plot
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.show()


diff_dir = NONE_DIFF_RESULTS_DIR / "statistics.json"
diff_data = load_json_file(diff_dir)
generate_stacked_bar_chart(diff_data)
