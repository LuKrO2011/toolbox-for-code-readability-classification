from datasets import load_from_disk

from readability_preprocessing.evaluation.utils import DATASET_DIR

ds = load_from_disk(DATASET_DIR)
ds_as_list = ds.to_list()

# Get the average "score" of the dataset
scores = [x['score'] for x in ds_as_list]
average_score = sum(scores) / len(scores)
print(average_score)
