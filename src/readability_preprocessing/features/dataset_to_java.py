import os

from datasets import load_dataset

from readability_preprocessing.dataset.dataset_combiner import _remove_ambiguous_samples

# Load the dataset from Hugging Face
ds = load_dataset("se2p/code-readability-merged")

# Define the output folder
output_folder = "/Users/lukas/Documents/Code_for_study/merged_well"
os.makedirs(output_folder, exist_ok=True)

# Remove ambiguous samples from the dataset
ds = ds["train"]
ds_as_list = ds.to_list()
filtered_ds = _remove_ambiguous_samples(ds, 0.5).to_list()

# Filter the dataset and get the 50% of the samples
# with the highest readability score from the filtered_ds
filtered_ds.sort(key=lambda x: x["score"], reverse=True)
filtered_ds = filtered_ds[: int(len(filtered_ds) / 2)]
# filtered_ds = sorted(filtered_ds, key=lambda x: x["score"])
# filtered_ds = filtered_ds[: int(len(filtered_ds) / 2)]

for i, record in enumerate(filtered_ds):
    # if record['score'] == 3.68:
    code_snippet = record["code_snippet"]
    # file_name = record['name']
    file_name = f"{str(i)}.java"

    # Define the output path with the corresponding name
    output_path = os.path.join(output_folder, f"{file_name}.java")

    # Write the code snippet to the file
    with open(output_path, "w") as file:
        file.write(code_snippet)

print(f"Code snippets saved to {output_folder}")
