import random

from datasets import load_dataset, Dataset


def balance_dataset(dataset: list[dict]) -> list[dict]:
    """
    Balances the dataset by making sure each score has the same amount of samples.
    :param dataset: The dataset to balance.
    :return: The balanced dataset.
    """
    # Get the number of samples for each score
    scores = [x['score'] for x in dataset]
    score_counts = {score: scores.count(score) for score in set(scores)}

    # Get the score with the least amount of samples
    min_score = min(score_counts, key=score_counts.get)
    min_count = score_counts[min_score]

    # Get the score with the most amount of samples
    max_score = max(score_counts, key=score_counts.get)
    max_count = score_counts[max_score]

    # Print the number of samples to remove
    for score, count in score_counts.items():
        print(f"Score: {score}, Count: {count}, Remove: {count - min_count}")

    # Balance the dataset
    balanced_dataset = []
    for score in set(scores):
        # Get the samples with the current score
        samples = [x for x in dataset if x['score'] == score]

        if score_counts[score] == min_count:
            # If the score has min count, add all
            balanced_dataset.extend(samples)
        else:
            # If the score has more than min count, add a random sample
            balanced_dataset.extend(random.sample(samples, min_count))

    return balanced_dataset


def filter_out_duplicates(dataset: dict[str, dict]) -> dict[str, dict]:
    """
    Filters out duplicates from the dataset.
    For each name without "_rdh" in the end, check if there is a name with "_rdh" in the
    end. If there is, compare the code_snippets of the two samples. If they are the same,
    remove both samples from the dataset.
    :param dataset: The dataset to filter.
    :return: The filtered dataset.
    """
    # Get all the names with and without "_rdh" in the end
    names = list(dataset.keys())
    names_without_rdh = [name for name in names if not name.endswith("_rdh")]
    names_with_rdh = [name for name in names if name.endswith("_rdh")]

    # Build pairs of names with and without "_rdh" in the end
    pairs = []
    for name in names_without_rdh:
        if name + "_rdh" in names_with_rdh:
            pairs.append((name, name + "_rdh"))

    # Remove the pairs with the same code snippet
    num_removed = 0
    filtered_dataset = {}
    for name, sample in dataset.items():
        is_rdh = name.endswith("_rdh")
        pair_name = (name[:-4], name) if is_rdh else (name, name + "_rdh")

        # If the sample is not in a pair, add it to the filtered dataset
        if pair_name not in pairs:
            filtered_dataset.update({name: sample})

        # If the sample is in a pair, check if the code snippets are the same
        else:
            pair_samples = [dataset[name] for name in pair_name]
            if pair_samples[0]['code_snippet'] != pair_samples[1]['code_snippet']:
                filtered_dataset.update({name: sample})
            else:
                num_removed += 1

    print(f"Removed {num_removed} duplicates")

    return filtered_dataset


random.seed(42)
ds = load_dataset("se2p/code-readability-krod")  # download_mode="force_redownload",
#                   verification_mode=VerificationMode.NO_CHECKS)
ds = ds['train']
ds_as_list = ds.to_list()
ds_dict = {x['name']: x for x in ds_as_list}
ds_without_duplicates = filter_out_duplicates(ds_dict)
ds_without_duplicates_as_list = list(ds_without_duplicates.values())
balanced_ds = balance_dataset(ds_without_duplicates_as_list)

# Store the dataset locally
# ds = Dataset.from_list(balanced_ds)
# ds.save_to_disk("LuKrO/code-readability-krod-balanced")

# Store the dataset in the HuggingFace Hub
# ds = Dataset.from_list(balanced_ds)
# ds.push_to_hub("LuKrO/code-readability-krod-balanced", private=True)
