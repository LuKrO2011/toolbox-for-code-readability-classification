import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats
from scipy.stats import zscore

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)


def ttest_ind(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """
    Perform a t-test for the means of two independent samples of scores.
    :param a: The first set of scores.
    :param b: The second set of scores.
    :return: Tuple containing the t-statistic and the p-value.
    """
    if len(a) > 1 and len(b) > 1:
        t_statistic, p_value = stats.ttest_ind(a, b)
        return t_statistic, p_value
    return np.nan, np.nan  # Not enough data to perform t-test


def load_and_preprocess_data(paths: dict[str, str]) -> dict[str, pd.DataFrame]:
    """
    Load and preprocess feature datasets from given paths.
    :param paths: A dictionary of dataset names and their corresponding file paths.
    :return: A dictionary of preprocessed DataFrames.
    """
    dataframes = {}
    for name, path in paths.items():
        try:
            dataset = pd.read_csv(path)
            dataset = remove_filename_column(dataset)
            dataset = handle_nans(dataset)
            dataframes[name] = dataset
        except Exception as e:
            print(f"Error loading {name}: {e}")
    return dataframes


def perform_statistical_tests(
    datasets: dict[str, pd.DataFrame], normalize: bool = True
) -> pd.DataFrame:
    """
    Perform statistical significance tests (t-tests) on the datasets.
    :param datasets: A dictionary of dataset names and their DataFrames.
    :param normalize: Flag to enable Z-score normalization.
    :return: A DataFrame containing p-values and additional statistics
    for each dataset comparison.
    """
    result_records = []
    dataset_names = list(datasets.keys())

    for i in range(len(dataset_names)):
        for j in range(len(dataset_names)):
            if i == j:
                continue

            name1, name2 = dataset_names[i], dataset_names[j]
            common_columns = datasets[name1].columns.intersection(
                datasets[name2].columns
            )

            if not common_columns.empty:
                for column in common_columns:
                    col1 = datasets[name1][column]
                    col2 = datasets[name2][column]

                    # Normalize if the flag is set
                    if normalize:
                        col1 = zscore(col1)
                        col2 = zscore(col2)

                    # Perform the t-test
                    t_statistic, p_value = ttest_ind(col1, col2)

                    # Store the results
                    result_records.append(
                        {
                            "Feature": column,
                            "Dataset1": name1,
                            "Dataset2": name2,
                            "t-statistic": t_statistic,
                            "p-value": p_value,
                        }
                    )

    # Create a DataFrame from the records
    return pd.DataFrame(result_records)


def plot_results(results: pd.DataFrame):
    """
    Plot the statistical test results as boxplots and heatmaps.
    :param results: A DataFrame containing result statistics
    for each dataset comparison.
    """
    # Pivot table for heatmap
    heatmap_data = results.pivot_table(
        index="Feature", columns=["Dataset1", "Dataset2"], values="p-value"
    )

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,
        cmap="coolwarm",
        fmt=".2g",
        cbar_kws={"label": "p-value"},
    )
    plt.title("Statistical Significance Test P-values Heatmap")
    plt.xlabel("Dataset Comparison")
    plt.ylabel("Features")
    plt.show()

    # Optional: Boxplot of p-values
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=results, x="Feature", y="p-value", hue="Dataset1")
    plt.xticks(rotation=45)
    plt.title("P-values by Feature")
    plt.ylabel("P-value")
    plt.xlabel("Feature")
    plt.legend(title="Dataset")
    plt.show()


if __name__ == "__main__":
    # Fix the seed for reproducibility
    np.random.seed(42)

    dataset_paths = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "krod_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "krod_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    # Load and preprocess data
    preprocessed_data = load_and_preprocess_data(dataset_paths)

    # Perform statistical tests
    test_results = perform_statistical_tests(preprocessed_data)

    # Display results
    print(test_results)

    # Plot the results
    plot_results(test_results)
