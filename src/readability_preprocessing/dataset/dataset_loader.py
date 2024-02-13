from datasets import load_dataset

# ds = load_dataset("se2p/code-readability-krod")
ds = load_dataset("LuKrO/code-readability-krod-balanced")
ds = ds['train']
ds_as_list = ds.to_list()

# Get the average "score" of the dataset
scores = [x['score'] for x in ds_as_list]
average_score = sum(scores) / len(scores)
print(average_score)

# Print the number of samples with a score of 4.5
count = 0
for x in ds_as_list:
    if x['score'] == 4.5:
        count += 1
print(f"Number of samples with a score of 4.5: {count}")

# Print the number of samples with a score of 1.5
count = 0
for x in ds_as_list:
    if x['score'] == 1.5:
        count += 1
print(f"Number of samples with a score of 1.5: {count}")
