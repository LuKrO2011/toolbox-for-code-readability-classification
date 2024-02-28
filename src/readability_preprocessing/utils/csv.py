import logging
import os

HEADER_PATH = os.path.join(os.path.dirname(__file__), "../../res/header.csv")


def append_features_to_csv(
    filename: str, snippet_path: str, features: dict[str, float]
) -> None:
    """
    Append the extracted features to a CSV file.
    :param filename: The path to the CSV file
    :param snippet_path: The path to the Java code snippet
    :param features: The extracted features
    :return: None
    """
    # Check if the CSV file already exists
    csv_file_exists = os.path.isfile(filename)

    # Append the features to the CSV file
    with open(filename, "a") as csv_file:
        # Write the header, if the CSV file does not exist
        if not csv_file_exists:
            header = load_header()
            csv_file.write(",".join(header) + "\n")

        # Append the feature to the CSV file
        csv_file.write(f"{snippet_path},")
        for idx, feature_value in enumerate(features.values()):
            csv_file.write(str(feature_value))
            if idx != len(features) - 1:
                csv_file.write(",")
        csv_file.write("\n")


def load_features_from_csv(csv_file_path: str) -> dict[str, dict[str, float]]:
    """
    Load the extracted features from a CSV file.
    :param csv_file_path: The path to the CSV file
    :return: The extracted features
    """
    # Check if the CSV file exists
    if not os.path.isfile(csv_file_path):
        raise ValueError(f"CSV file does not exist: {csv_file_path}")

    # Load the features from the CSV file
    features = {}
    with open(csv_file_path) as csv_file:
        # Read the header
        header = csv_file.readline().strip().split(",")

        # Read the features
        for line in csv_file:
            # Create a dictionary to store the features
            feature_data = {}

            # Read the features
            feature_values = line.strip().split(",")
            for idx, feature_name in enumerate(header[1:]):
                feature_value = feature_values[idx + 1]
                feature_value = float(feature_value)
                feature_data[feature_name] = feature_value

            # Add the features to the list
            if feature_data:  # Do not add empty entries
                features.update({feature_values[0]: feature_data})

    logging.info(f"Loaded features from {csv_file_path}.")

    return features


def load_header(path: str = HEADER_PATH) -> list[str]:
    """
    Load the header of the CSV file.
    :param path: The path to the CSV file
    :return: The header of the CSV file
    """
    # Load the header
    with open(path) as header_file:
        return header_file.readline().strip().split(",")
