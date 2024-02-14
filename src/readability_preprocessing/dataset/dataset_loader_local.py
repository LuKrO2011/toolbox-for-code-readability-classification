from datasets import load_from_disk

from readability_preprocessing.evaluation.utils import PROLIFIC_DIR

ds = load_from_disk(PROLIFIC_DIR / "dataset_score")
ds_as_list = ds.to_list()

# Get the average "score" of the dataset
scores = [x['score'] for x in ds_as_list]
average_score = sum(scores) / len(scores)
print(average_score)

# # Upload the dataset to Hugging Face
# dataset_name = "LuKrO/code-readability-krod-survey"
# ds.push_to_hub(dataset_name)
