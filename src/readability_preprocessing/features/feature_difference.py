import numpy as np

from readability_preprocessing.utils.csv import load_features_from_csv

# path1 = "/Users/lukas/Documents/Code for Study/features.csv"
# path2 = "/Users/lukas/Desktop/features.csv"

epsilon = 1e-6
path1 = "../../tests/res/csv/features.csv"
path2 = "../../tests/res/csv/features2.csv"

# Load features from CSV
features1: dict[str, dict[str, float]] = load_features_from_csv(path1)
features2: dict[str, dict[str, float]] = load_features_from_csv(path2)

# Convert the dict[str, dict[str, float]] to list[list[float]]
converted_features1 = [list(features.values()) for features in features1.values()]
converted_features2 = [list(features.values()) for features in features2.values()]

# Remove NaNs from the features
features_array1 = np.array(converted_features1)
without_nans1 = np.nan_to_num(features_array1)
features_array2 = np.array(converted_features2)
without_nans2 = np.nan_to_num(features_array2)

# Normalize the features
normalized_features1 = without_nans1 / (np.linalg.norm(without_nans1, axis=0) + epsilon)
normalized_features2 = without_nans2 / (np.linalg.norm(without_nans2, axis=0) + epsilon)

# Calculate the average (mean of features across rows)
average_features1 = normalized_features1.mean(axis=0)
average_features2 = normalized_features2.mean(axis=0)

# Calculate the sum of the features
sum_features1 = without_nans1.sum(axis=0)
sum_features2 = without_nans2.sum(axis=0)

# Calculate the absolute differences
absolute_differences = abs(sum_features2 - sum_features1)

# Calculate internal standard deviation for both feature sets
std_internal_relative1 = normalized_features1.std(axis=0)
std_internal_relative2 = normalized_features2.std(axis=0)
std_internal_absolute1 = without_nans1.std(axis=0)
std_internal_absolute2 = without_nans2.std(axis=0)

# Calculate the external standard deviation (between the two sets)
external_std_relative = np.sqrt(
    (std_internal_relative1**2 + std_internal_relative2**2) / 2
)
external_std_absolute = np.sqrt(
    (std_internal_absolute1**2 + std_internal_absolute2**2) / 2
)

# Compare the two feature sets: Get the column names with the highest
feature_names = list(list(features1.values())[0].keys())
feature_differences = abs(average_features1 - average_features2)

# Get indices for top 5 features with the highest differences
sorted_indices = np.argsort(feature_differences)
top_5_indices = sorted_indices[-5:][::-1]  # Indices of the top 5 largest

# Get all features of the top 5 indices
top_5_features = [
    (
        feature_names[idx],
        feature_differences[idx],
        absolute_differences[idx],
        std_internal_relative1[idx],
        std_internal_absolute1[idx],
        std_internal_relative2[idx],
        std_internal_absolute2[idx],
        external_std_relative[idx],
        external_std_absolute[idx],
    )
    for idx in top_5_indices
]

# Print the top 5 features with differences
print("Top 5 features with the highest differences (based on average):")
print(
    f"{'Feature':<30} {'Mean Diff':<15} {'Abs Diff':<15} {'Std Rel 1':<15} "
    f"{'Std Abs 1':<15} {'Std Rel 2':<15} {'Std Abs 2':<15} "
    f"{'Ext Std Rel':<15} {'Ext Std Abs':<15}"
)
for feature in top_5_features:
    print(
        f"{feature[0]:<30} {feature[1]:<15.4f} {feature[2]:<15.4f}"
        f"{feature[3]:<15.4f} {feature[4]:<15.4f} {feature[5]:<15.4f}"
        f"{feature[6]:<15.4f} {feature[7]:<15.4f} {feature[8]:<15.4f}"
    )

# Print the feature names for all features with a difference of 0
zero_difference_indices = np.where(feature_differences < epsilon)
zero_difference_features = [feature_names[idx] for idx in zero_difference_indices[0]]
print("\nFeatures with a difference of 0:")
print(zero_difference_features)
