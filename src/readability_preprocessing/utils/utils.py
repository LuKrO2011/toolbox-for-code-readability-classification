import logging
import os
import shutil
from pathlib import Path
from typing import List, Any

import yaml
from yaml import SafeLoader


def store_as_txt(stratas: List[List[str]], output_dir: str) -> None:
    """
    Store the sampled Java code snippet paths in a txt file.
    :param stratas: The sampled Java code snippet paths
    :param output_dir: The directory where the txt file should be stored
    :return: None
    """
    with open(os.path.join(output_dir, "stratas.txt"), "w") as file:
        for idx, stratum in enumerate(stratas):
            file.write(f"Stratum {idx}:\n")
            for snippet in stratum:
                file.write(f"{snippet}\n")


def list_java_files(directory: str) -> List[str]:
    """
    List all Java files in a directory.
    :param directory: The directory to search for Java files
    :return: A list of Java files
    """
    java_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.abspath(os.path.join(root, file)))

    return java_files


def load_code(file: str) -> str:
    """
    Loads the code from a file.
    :param file: Path to the file.
    :return: Code.
    """
    with open(file) as file:
        return file.read()


def image_to_bytes(image_path: str) -> bytes:
    """
    Converts an image to bytes.
    :param image_path: The path to the image
    :return: The image as bytes
    """
    with open(image_path, "rb") as f:
        return f.read()


def bytes_to_image(image: bytes, image_path: str) -> None:
    """
    Converts bytes to an image.
    :param image: The image as bytes
    :param image_path: The path where the image should be stored
    :return: None
    """
    with open(image_path, "wb") as f:
        f.write(image)


def copy_files(from_dir: str, to_dir: str) -> None:
    """
    Copies all files from directory.
    :param from_dir: The directory to copy from.
    :param to_dir: The directory to copy to.
    :return: None
    """
    for file in os.listdir(from_dir):
        from_file = os.path.join(from_dir, file)
        to_file = os.path.join(to_dir, file)
        if os.path.isfile(from_file):
            shutil.copy2(from_file, to_file)


def num_files(dir: str) -> int:
    """
    Counts the number of files in a directory and all its subdirectories.
    :param dir: The directory to count the files in.
    :return: The number of files.
    """
    num_files = 0
    for root, dirs, files in os.walk(dir):
        num_files += len(files)
    return num_files


def list_non_hidden(dir: str) -> list[str]:
    """
    List the non-hidden files in the given directory. Also ignores .log files.
    :param dir: The directory to list the files from.
    :return: The list of non-hidden files.
    """
    return [f for f in os.listdir(dir) if
            not f.startswith(".") and not f.endswith(".log")]


def load_yaml_file(path: Path) -> dict[str, Any]:
    """
    Loads a yaml file to a dict.
    :param path: The path to the yaml file.
    :return: Returns the loaded yaml as dict.
    """
    # Read file
    try:
        raw_str = path.read_text()
    except FileNotFoundError:
        logging.warning(f"Yaml file {path} not found.")
        return {}

    # Parse yaml
    try:
        dic = yaml.load(raw_str, Loader=SafeLoader)
    except yaml.YAMLError as e:
        logging.warning(f"Yaml file {path} could not be parsed.")
        logging.warning(e)
        return {}

    # Return dict
    if dic is None:
        return {}
    return dic


def load_txt_file(path: Path) -> List[str]:
    """
    Loads a txt file line by line to a list of strings.
    :param path: The path to the txt file.
    :return: Returns the loaded txt as list of strings.
    """
    # Read file
    with open(path, "r") as file:
        lines = file.readlines()

    # Return list
    return [line.strip() for line in lines]
