from matplotlib import pyplot as plt

from readability_preprocessing.evaluation.utils import load_snippet_datas, SnippetData


def create_combined_box_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a single plot with multiple box plots for the rates of all snippets
    :param snippet_datas: The list of all snippets
    :return: None
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


def create_combined_violin_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a single plot with multiple violin plots for the rates of all snippets
    :param snippet_datas: The list of all snippets
    :return: None
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Create the violin plot
    plt.figure(figsize=(6, 8))
    plt.violinplot(ratings)
    plt.xticks(range(1, len(snippet_datas) + 1),
               [snippet_data.path for snippet_data in snippet_datas])
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Show the plot
    plt.show()


def extract_name(path: str) -> str:
    """
    Extract the name of the snippet from the path. The path is separated by
    underscores.
    :param path: The path to the snippet
    :return: The name of the snippet
    """
    return path.split('_')[-1]


def create_mean_plot(snippet_datas: list[SnippetData]) -> None:
    """
    Create a plot of the mean of the ratings for each snippet
    :param snippet_datas: The list of all snippets
    :return: None
    """
    # Extract the ratings for each snippet
    ratings = [[rate.rate for rate in snippet_data.rates] for snippet_data in
               snippet_datas]

    # Calculate the mean of the ratings for each snippet
    means = [sum(rating) / len(rating) for rating in ratings]

    # Create the plot
    plt.figure(figsize=(6, 8))
    plt.plot(range(1, len(snippet_datas) + 1), means, 'o')
    plt.xticks(range(1, len(snippet_datas) + 1),
               [str(x) for x in range(1, len(snippet_datas) + 1)])
    plt.ylim(1, 5)
    plt.ylabel('Rating')
    plt.title('Rating of the snippets')

    # Annotate each point with the snippet name
    # for i, mean in enumerate(means):
    #     plt.annotate(extract_name(snippet_datas[i].path), (i + 1, mean))

    # Show the plot
    plt.show()


snippet_datas = load_snippet_datas()
create_mean_plot(snippet_datas)
