import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats

from readability_preprocessing.features.feature_difference import (
    handle_nans,
    remove_filename_column,
)

REMOVE_NAN_COLUMNS = True


def ttest_ind(a: list[float], b: list[float]) -> tuple[float, float]:
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
            if not REMOVE_NAN_COLUMNS:
                dataset = handle_nans(dataset)
            dataframes[name] = dataset
        except Exception as e:
            print(f"Error loading {name}: {e}")

    if REMOVE_NAN_COLUMNS:
        nan_columns = []

        # Gather all columns that contain NaN values across all datasets
        for dataset in dataframes.values():
            nan_columns.extend(dataset.columns[dataset.isna().any()].tolist())
        nan_columns = list(set(nan_columns))

        # Drop the columns and reassign the result to the dataset
        for key, dataset in dataframes.items():
            dataframes[key] = dataset.drop(nan_columns, axis=1)

    return dataframes


def perform_statistical_tests(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Perform statistical significance tests (t-tests) on the datasets.
    :param datasets: A dictionary of dataset names and their DataFrames.
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
                    col1 = datasets[name1][column].tolist()
                    col2 = datasets[name2][column].tolist()

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
    # Check the content of results DataFrame
    print("Results DataFrame:")
    print(results.head())
    print("Summary statistics:")
    print(results.describe())

    # Pivot table for heatmap
    heatmap_data = results.pivot_table(
        index="Feature",
        columns=["Dataset1", "Dataset2"],
        values="p-value",
        fill_value=1,
    )

    # Print the heatmap data to verify its correctness
    print("Heatmap Data (before plotting):")
    print(heatmap_data)

    # Create the heatmap using Matplotlib
    plt.figure(figsize=(17, 20))

    # Convert the heatmap data to a numpy array for plotting
    heatmap_array = heatmap_data.to_numpy()

    # Order the columns: merged(all)-m&m(all), merged_well-merged_badly,
    # m&m_well-m&m_badly, ...
    order = [
        "merged_all",
        "m&m_all",
        "merged_well",
        "merged_badly",
        "m&m_well",
        "m&m_badly",
    ]
    heatmap_data = heatmap_data.reindex(columns=order, level=0)
    heatmap_array = heatmap_data.to_numpy()

    # Create a color map
    cax = plt.imshow(heatmap_array, cmap="coolwarm", aspect="auto", vmin=0, vmax=1)

    # Set ticks and labels
    plt.xticks(
        ticks=np.arange(heatmap_array.shape[1]),
        labels=[f"{col[0]}-{col[1]}" for col in heatmap_data.columns],
    )
    plt.yticks(ticks=np.arange(heatmap_array.shape[0]), labels=heatmap_data.index)

    plt.colorbar(cax, label="p-value")
    plt.title("Blau = verschieden, Rot = gleich")
    plt.xlabel("Dataset Comparison")
    plt.ylabel("Features")

    # Optional: Limit to specific rows to reduce clutter
    plt.imshow(heatmap_array, cmap="coolwarm", aspect="auto", vmin=0, vmax=1)

    plt.tight_layout()
    plt.subplots_adjust(left=0.25)
    plt.show()


if __name__ == "__main__":
    # Fix the seed for reproducibility
    np.random.seed(42)

    dataset_paths = {
        "merged_well": "/Users/lukas/Documents/Features/features_merged_well.csv",
        "merged_badly": "/Users/lukas/Documents/Features/features_merged_badly.csv",
        "m&m_well": "/Users/lukas/Documents/Features/features_krod_well.csv",
        "m&m_badly": "/Users/lukas/Documents/Features/features_krod_badly.csv",
    }

    # Load and preprocess data
    preprocessed_data = load_and_preprocess_data(dataset_paths)

    # Add merged(all) and m&m(all) datasets
    preprocessed_data["merged_all"] = pd.concat(
        [preprocessed_data["merged_well"], preprocessed_data["merged_badly"]]
    )
    preprocessed_data["m&m_all"] = pd.concat(
        [preprocessed_data["m&m_well"], preprocessed_data["m&m_badly"]]
    )

    # Perform statistical tests
    test_results = perform_statistical_tests(preprocessed_data)

    # Display results
    print(test_results)

    # Define the data to plot (merged_well, merged_badly), (krod_well, krod_badly),
    # (merged_well, krod_well), (merged_badly, krod_badly)
    test_results = test_results[
        (
            (test_results["Dataset1"] == "merged_well")
            & (test_results["Dataset2"] == "merged_badly")
        )
        | (
            (test_results["Dataset1"] == "m&m_well")
            & (test_results["Dataset2"] == "m&m_badly")
        )
        | (
            (test_results["Dataset1"] == "merged_well")
            & (test_results["Dataset2"] == "m&m_well")
        )
        | (
            (test_results["Dataset1"] == "merged_badly")
            & (test_results["Dataset2"] == "m&m_badly")
        )
        | (
            (test_results["Dataset1"] == "merged_all")
            & (test_results["Dataset2"] == "m&m_all")
        )
    ]

    # Plot the results
    plot_results(test_results)
