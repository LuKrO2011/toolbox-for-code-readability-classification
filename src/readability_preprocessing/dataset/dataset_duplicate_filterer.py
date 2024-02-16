import random

from datasets import load_dataset


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
        else:
            print(f"Pair for {name} not found")

    # Remove the pairs with the same code snippet
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
                print(f"Duplicate code snippet for {name} and {pair_name[1]}")

    return filtered_dataset


random.seed(42)
ds = load_dataset("se2p/code-readability-krod")
ds = ds['train']
ds_as_list = ds.to_list()

# Convert the dataset to a dict with name as key
ds_dict = {x['name']: x for x in ds_as_list}

ds_without_duplicates = filter_out_duplicates(ds_dict)
pass

# Store the balanced dataset in the HuggingFace Hub
# ds = Dataset.from_list(balanced_ds)
# ds.push_to_hub("LuKrO/code-readability-krod-balanced", private=True)
