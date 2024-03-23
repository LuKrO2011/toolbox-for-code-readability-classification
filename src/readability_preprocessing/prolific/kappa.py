import numpy as np
import krippendorff

from readability_preprocessing.prolific.combiner import load_combined
from readability_preprocessing.prolific.extraction import extract_ratings

snippets = load_combined()
value_domain = [1, 2, 3, 4, 5]

# The ratings is a list of lists, where each list contains the ratings for a snippet
ratings = extract_ratings(snippets)

# Convert into np array
ratings = np.array(ratings).T

# Calculate the agreement
krippendorffs_alpha_score = krippendorff.alpha(ratings, value_domain=value_domain)

print(f"Krippendorff's Alpha: {krippendorffs_alpha_score}")
print()

# Example
ratings = np.array([[1, 1, 2, 1, 2], [4, 5, 5, 4, 5], [3, 3, 3, 3, 3], [2, 2, 1, 2, 1]]).T

krippendorffs_alpha_score = krippendorff.alpha(ratings, level_of_measurement="ordinal", value_domain=value_domain)
print(f"Krippendorff's Alpha: {krippendorffs_alpha_score}")
print()
