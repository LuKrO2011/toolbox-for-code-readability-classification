from readability_preprocessing.evaluation.utils import GROUPS_DIR, load_ids_from_txt

# Load the ids from the txt files
dir_path = GROUPS_DIR
ids = []
for file_path in dir_path.glob("*.txt"):
    new_ids = load_ids_from_txt(file_path)
    ids.extend(new_ids)

# Check if the ids are unique
ids_unique = len(ids) == len(set(ids))
print(f"Number of ids: {len(ids)}")
print(f"The ids are unique: {ids_unique}")
