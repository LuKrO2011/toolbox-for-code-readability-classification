import pandas as pd
from datasets import Dataset, load_dataset, load_from_disk


def _load_datasets(paths: list[str]) -> list[Dataset]:
    """
    Loads the datasets from the specified paths.
    :param paths: The paths to the datasets.
    :return: The datasets.
    """
    datasets = []
    for path in paths:
        dataset = load_from_disk(path)
        datasets.append(dataset)

    return datasets


def _remove_ambiguous_samples(
    dataset: Dataset, percent_to_remove: float = 0.5
) -> Dataset:
    """
    Removes the samples from the dataset that have an ambiguous readability score.
    Ambiguous readability scores are the percent_to_remove% in the middle of the
    dataset. Unambiguous readability scores are the (percent_to_remove/2)% with the
    lowest and the (percent_to_remove/2)% with the highest readability scores.
    :param dataset: The dataset.
    :param percent_to_remove: The percentage of samples to remove from the middle of the
    dataset.
    :return: The dataset without the ambiguous samples.
    """
    # Sort the dataset samples by readability score
    sorted_samples = sorted(dataset, key=lambda x: x["score"])

    # Calculate the number of samples to remove from the start and end
    num_samples = len(sorted_samples)
    num_to_remove = int(num_samples * percent_to_remove)
    num_to_remove_from_start_and_end = int(num_to_remove / 2)

    # Get the indices of samples to be kept (lowest 25% and highest 25%)
    indices_to_keep = set(range(num_to_remove_from_start_and_end)).union(
        set(range(num_samples - num_to_remove_from_start_and_end, num_samples))
    )

    # Create a new dataset without the ambiguous samples
    filtered_samples = [
        sample for i, sample in enumerate(sorted_samples) if i in indices_to_keep
    ]

    return dataset.from_list(filtered_samples)


def combine_datasets(
    dataset_paths: list[str], output_path: str, percent_to_remove: float | None = 0.5
) -> None:
    """
    Combines the datasets from the specified paths and saves the combined dataset to
    the output path.
    :param dataset_paths: The paths to the datasets.
    :param percent_to_remove: The percentage of ambiguous samples to remove from the
    dataset. If None, no samples are removed.
    :param output_path: The output path.
    """
    datasets = _load_datasets(dataset_paths)
    if percent_to_remove is not None:
        datasets = [
            _remove_ambiguous_samples(dataset, percent_to_remove)
            for dataset in datasets
        ]

    # Convert the datasets to pandas dataframes
    dfs = [dataset.to_pandas() for dataset in datasets]

    # Concatenate the dataframes
    combined_df = pd.concat(dfs)

    # Convert the dataframe to a dataset
    combined_dataset = Dataset.from_pandas(combined_df)

    combined_dataset.save_to_disk(output_path)


if __name__ == "__main__":
    # dataset_name = "dataset_with_names"
    # dorn_path = Path(
    #     "Somepath/Datasets/"
    #     "DatasetDornJava/dataset/" + dataset_name
    # )
    # bw_path = Path(
    #     "Somepath/Datasets/DatasetBW/"
    #     + dataset_name
    # )
    # scalabrio_path = Path(
    #     "Somepath/Datasets/"
    #     "Dataset/Dataset/" + dataset_name
    # )
    # combined_path = Path(
    #     "Somepath/Datasets/Combined"
    # )
    #
    # combine_datasets([dorn_path, bw_path, scalabrio_path], combined_path, None)

    ds = load_dataset("LuKrO/code-readability-mmm")  # download_mode="force_redownload",
    #                   verification_mode=VerificationMode.NO_CHECKS)
    ds = ds["train"]
    ds_as_list = ds.to_list()
    unambiguous = _remove_ambiguous_samples(ds, 0.5).to_list()

    # Store the dataset
    # ds = Dataset.from_list(unambiguous)
    # ds.save_to_disk("LuKrO/code-readability-mmm-unambiguous")
    ds = Dataset.from_list(unambiguous)
    ds.push_to_hub("LuKrO/code-readability-mmm-unambiguous", private=True)
