# Normalize the features and convert to a np array

from numpy import ndarray

from readability_preprocessing.sampling.stratified_sampling import _normalize_features
from readability_preprocessing.utils.csv import load_features_from_csv

# path1 = "/Users/lukas/Documents/Code for Study/features.csv"
# path2 = "/Users/lukas/Desktop/features.csv"

path1 = "../../tests/res/csv/features.csv"
path2 = "../../tests/res/csv/features2.csv"

features1:dict[str, dict[str, float]] = load_features_from_csv(path1)
features2:dict[str, dict[str, float]] = load_features_from_csv(path2)

# Convert the dict[str, dict[str, float]] to list[list[float]]
converted_features1 = [[value for value in features.values()] for features in features1.values()]
converted_features2 = [[value for value in features.values()] for features in features2.values()]

normalized_features1:ndarray[[float]] = _normalize_features(converted_features1)
normalized_features2:ndarray[[float]] = _normalize_features(converted_features2)

# Sum the features over all rows and divide by the number of rows
sum_features1 = normalized_features1.sum(axis=0)
sum_features2 = normalized_features2.sum(axis=0)

# Compare the two feature sets: Get the colum names with the highest difference
feature_names = list(list(features1.values())[0].keys())
feature_differences = abs(sum_features1 - sum_features2)
max_difference_idx = feature_differences.argmax()
max_difference_feature = feature_names[max_difference_idx]

print(f"The feature with the highest difference is '{max_difference_feature}' with a difference of {feature_differences[max_difference_idx]}")

