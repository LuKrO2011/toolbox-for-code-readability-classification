from numpy import ndarray
import numpy as np
from readability_preprocessing.sampling.stratified_sampling import _normalize_features
from readability_preprocessing.utils.csv import load_features_from_csv

# path1 = "/Users/lukas/Documents/Code for Study/features.csv"
# path2 = "/Users/lukas/Desktop/features.csv"

path1 = "../../tests/res/csv/features.csv"
path2 = "../../tests/res/csv/features2.csv"

# Load features from CSV
features1:dict[str, dict[str, float]] = load_features_from_csv(path1)
features2:dict[str, dict[str, float]] = load_features_from_csv(path2)

# Convert the dict[str, dict[str, float]] to list[list[float]]
converted_features1 = [[value for value in features.values()] for features in features1.values()]
converted_features2 = [[value for value in features.values()] for features in features2.values()]

# Normalize features
normalized_features1:ndarray[[float]] = _normalize_features(converted_features1)
normalized_features2:ndarray[[float]] = _normalize_features(converted_features2)

# Calculate the average (sum of features divided by the number of rows)
average_features1 = normalized_features1.mean(axis=0)
average_features2 = normalized_features2.mean(axis=0)

# Compare the two feature sets: Get the column names with the highest and lowest differences
feature_names = list(list(features1.values())[0].keys())
feature_differences = abs(average_features1 - average_features2)

# Get indices for top 5 and lowest 5 differences
sorted_indices = np.argsort(feature_differences)
top_5_indices = sorted_indices[-5:][::-1]  # Indices of the top 5 largest differences
lowest_5_indices = sorted_indices[:5]      # Indices of the 5 smallest differences

# Get the feature names and differences for the top 5
top_5_features = [(feature_names[idx], feature_differences[idx]) for idx in top_5_indices]

# Print the top 5 and lowest 5 features with differences
print("Top 5 features with the highest differences (based on average):")
for feature, difference in top_5_features:
    print(f"Feature: '{feature}' with a difference of {difference}")

# Print the feature names for all features with a difference of 0
epsilon = 1e-6
zero_difference_indices = np.where(feature_differences < epsilon)
zero_difference_features = [feature_names[idx] for idx in zero_difference_indices[0]]
print("\nFeatures with a difference of 0:")
print(zero_difference_features)
