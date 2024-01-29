import matplotlib.pyplot as plt

from readability_preprocessing.evaluation.utils import NONE_DIFF_RESULTS_DIR, \
    load_json_file


def generate_bar_chart(data: list) -> None:
    """
    Generates a bar chart for the relative frequency of 'not_different' cases overall,
    for each stratum, and for each stratum and rdh.
    :param data: The data containing the relative frequency of 'not_different' cases
    """
    # Extract relevant data for plotting
    strata_labels = [entry["stratum"] for entry in data]
    not_different = [entry["not_different_rel"] for entry in data]

    # Create a bar chart for 'different' cases
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.bar(strata_labels, not_different, color='lightcoral', edgecolor='black')

    # Adding labels, title, and legend
    plt.xlabel('Stratum')
    plt.ylabel('Relative Frequency')
    plt.title('Relative Frequency of Not Different Cases')

    # Display the percentage values on top of the bars
    for i, v in enumerate(not_different):
        plt.text(i, v, f'{v:.2%}', ha='center', va='bottom', color='black',
                 fontweight='bold')

    # Show the plot
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.show()


diff_dir = NONE_DIFF_RESULTS_DIR / "statistics.json"
diff_data = load_json_file(diff_dir)
generate_bar_chart(diff_data)
