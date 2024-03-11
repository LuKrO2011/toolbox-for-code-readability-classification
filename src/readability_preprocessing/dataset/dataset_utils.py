import random

from datasets import load_dataset


def balance_dataset(dataset: list[dict]) -> list[dict]:
    """
    Balances the dataset by making sure each score has the same amount of samples.
    :param dataset: The dataset to balance.
    :return: The balanced dataset.
    """
    # Get the number of samples for each score
    scores = [x["score"] for x in dataset]
    score_counts = {score: scores.count(score) for score in set(scores)}

    # Get the score with the least amount of samples
    min_score = min(score_counts, key=score_counts.get)
    min_count = score_counts[min_score]

    # Get the score with the most amount of samples
    max_score = max(score_counts, key=score_counts.get)
    score_counts[max_score]

    # Print the number of samples to remove
    for score, count in score_counts.items():
        print(f"Score: {score}, Count: {count}, Remove: {count - min_count}")

    # Balance the dataset
    balanced_dataset = []
    for score in set(scores):
        # Get the samples with the current score
        samples = [x for x in dataset if x["score"] == score]

        if score_counts[score] == min_count:
            # If the score has min count, add all
            balanced_dataset.extend(samples)
        else:
            # If the score has more than min count, add a random sample
            balanced_dataset.extend(random.sample(samples, min_count))

    return balanced_dataset


def fileter_out_duplicates(
    dataset: dict[str, dict], original_score: float = 3.68
) -> dict[str, dict]:
    """
    Filters out duplicates from the dataset.
    All code_snippets are sorted by their content and then compared.
    :param dataset: The dataset to filter.
    :param original_score: The score to keep if there are duplicates.
    :return: The filtered dataset.
    """
    # Sort the dataset by code_snippet and by score (original_score first)
    sorted_dataset = sorted(
        dataset.items(),
        key=lambda x: (x[1]["code_snippet"], x[1]["score"]),
        reverse=True,
    )

    # Remove the duplicates. Always keep the first sample.
    filtered_dataset = {}
    num_removed_original = 0
    num_removed_modified = 0
    for i in range(len(sorted_dataset)):
        name, sample = sorted_dataset[i]
        if i == 0:
            filtered_dataset.update({name: sample})
        else:
            prev_name, prev_sample = sorted_dataset[i - 1]
            if sample["code_snippet"] == prev_sample["code_snippet"]:
                if sample["score"] == original_score:
                    num_removed_original += 1
                else:
                    num_removed_modified += 1
            else:
                filtered_dataset.update({name: sample})

    # Print the number of removed duplicates
    print(f"Removed {num_removed_original} duplicates with a score of {original_score}")
    print(
        f"Removed {num_removed_modified} duplicates with a score different from "
        f"{original_score}"
    )

    return filtered_dataset


random.seed(42)
ds = load_dataset(
    "LuKrO/code-readability-krod-strong8"
)  # download_mode="force_redownload",
#                   verification_mode=VerificationMode.NO_CHECKS)
ds = ds["train"]
ds_as_list = ds.to_list()
ds_dict = {x["name"]: x for x in ds_as_list}
ds_without_duplicates = fileter_out_duplicates(ds_dict)
ds_without_duplicates_as_list = list(ds_without_duplicates.values())
balanced_ds = balance_dataset(ds_without_duplicates_as_list)

# Store the dataset locally
# ds = Dataset.from_list(balanced_ds)
# ds.save_to_disk("LuKrO/code-readability-krod-strong5-balanced")

# Store the dataset in the HuggingFace Hub
# ds = Dataset.from_list(balanced_ds)
# ds.push_to_hub("LuKrO/code-readability-krod-strong8-balanced", private=True)
