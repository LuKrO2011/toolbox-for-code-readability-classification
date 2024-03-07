from datasets import concatenate_datasets, load_dataset

# Names of the datasets to combine
ds1_name = "se2p/code-readability-merged"
ds2_name = "LuKrO/code-readability-krod-survey"
combined_ds_name = "LuKrO/code-readability-mmm"

# Load and combine the datasets
ds1 = load_dataset(ds1_name)["train"]
ds2 = load_dataset(ds2_name)["train"]
combined_dataset = concatenate_datasets([ds1, ds2])
print(f"Combined dataset: {combined_dataset}")

# Push the combined dataset to the hub
# combined_dataset.push_to_hub(combined_ds_name, private=True)
