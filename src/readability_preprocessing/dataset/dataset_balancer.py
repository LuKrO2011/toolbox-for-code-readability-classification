import random

from datasets import load_dataset
from datasets import Dataset

from readability_preprocessing.utils.dataset import upload_dataset


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


random.seed(42)
ds = load_dataset("se2p/code-readability-krod")
ds = ds['train']
ds_as_list = ds.to_list()
balanced_ds = balance_dataset(ds_as_list)

# Store the balanced dataset in the HuggingFace Hub
ds = Dataset.from_list(balanced_ds)
ds.push_to_hub("LuKrO/code-readability-krod-balanced", private=True)
