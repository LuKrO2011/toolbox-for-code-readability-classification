import json

import pandas as pd


def load_json_file(file_path):
    """
    Load and parse JSON content from a file
    :param file_path: The path to the JSON file
    :return: A Python object parsed from the JSON file
    """
    with open(file_path) as file:
        return json.load(file)


def load_csv_file(file_path):
    """
    Load and parse a CSV file as a DataFrame
    :param file_path: The path to the CSV file
    :return: The parsed CSV file as a DataFrame
    """
    return pd.read_csv(file_path)


def load_csv_files(file_paths):
    """
    Load and combine multiple CSV files into a single DataFrame
    :param file_paths: The paths to the CSV files
    :return: The combined CSV files as a DataFrame
    """
    return pd.concat(
        [load_csv_file(file_path) for file_path in file_paths], ignore_index=True
    )
