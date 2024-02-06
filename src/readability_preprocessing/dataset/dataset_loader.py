from datasets import load_dataset
ds = load_dataset("se2p/code-readability-merged")
ds = ds['train']
ds_as_list = ds.to_list()

# Get the average "score" of the dataset
scores = [x['score'] for x in ds_as_list]
average_score = sum(scores) / len(scores)
print(average_score)
