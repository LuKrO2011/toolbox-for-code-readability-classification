from matplotlib import pyplot as plt

from readability_preprocessing.evaluation.utils import load_snippet_datas, SnippetData


def create_combined_box_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a single plot with multiple box plots for the rates of all snippets
    :param snippet_datas: The list of all snippets
    :return: The combined box plot
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Create the box plot
    plt.figure(figsize=(6, 8))
    plt.boxplot(ratings)
    plt.xticks(range(1, len(snippet_datas) + 1),
               [snippet_data.path for snippet_data in snippet_datas])
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Show the plot
    plt.show()


snippet_datas = load_snippet_datas()
# for snippet_data in snippet_datas:
#     snippet_data.create_box_plot()
create_combined_box_plot(snippet_datas)
