import logging
import os

from datasets import load_from_disk, load_dataset
from huggingface_hub import login

from src.readability_preprocessing.utils.utils import image_to_bytes


def add_images_to_dataset(images_dir: str, dataset_without_images: str,
                          dataset_with_images: str) -> None:
    """
    Converts a directory with images to a HuggingFace dataset.
    :param images_dir: The directory containing the images
    :param dataset_without_images: The directory containing the HuggingFace dataset
     without images
    :param dataset_with_images: The directory where the HuggingFace dataset with images
     should be stored
    :return: None
    """
    # Load the existing HuggingFace dataset without images
    dataset = load_from_disk(dataset_without_images)

    # Convert the images to bytes
    images = [image_to_bytes(os.path.join(images_dir, f"{idx}.java.png")) for
              idx in range(len(dataset))]

    # Add the image column to the dataset
    dataset = dataset.add_column("image", images)

    # Save the dataset
    dataset.save_to_disk(dataset_with_images)


def is_huggingface_dataset(directory: str) -> bool:
    """
    Checks if a directory is a HuggingFace dataset.
    :param directory: The directory to check
    :return: True if the directory is a HuggingFace dataset, False otherwise
    """
    return os.path.isfile(os.path.join(directory, "dataset_info.json"))


def generate_java_files_from_dataset(dataset_dir: str,
                                     java_files_dir: str) -> None:
    """
    Generates Java files from a HuggingFace dataset.
    :param dataset_dir: The directory containing the HuggingFace dataset
    :param java_files_dir: The directory where the Java files should be stored
    :return: None
    """
    # Load the dataset
    dataset = load_from_disk(dataset_dir)

    # Generate the Java files
    for idx, data in enumerate(dataset):
        code = data["code_snippet"]
        file_path = os.path.join(java_files_dir, f"{idx}.java")
        with open(file_path, "w") as file:
            file.write(code)

    logging.info(f"Generated {len(dataset)} Java files from the HuggingFace dataset.")


def get_huggingface_token(file_path: str) -> str:
    """
    Reads the HuggingFace token from a file.
    :param file_path: Path to the file containing the token
    :return: HuggingFace token
    """
    with open(file_path, 'r') as file:
        token = file.read().strip()
    return token


def upload_dataset(dataset_dir: str, dataset_name: str, token_file: str) -> None:
    """
    Uploads a HuggingFace dataset to the HuggingFace Hub.
    :param dataset_dir: The directory containing the HuggingFace dataset
    :param dataset_name: The name of the dataset
    :param token_file: Path to the file containing your HuggingFace token
    :return: None
    """
    huggingface_token = get_huggingface_token(token_file)
    login(token=huggingface_token)
    dataset = load_from_disk(dataset_dir)
    dataset.push_to_hub(dataset_name)
    logging.info(f"Uploaded dataset '{dataset_name}' to the HuggingFace Hub.")


def download_dataset(dataset_name: str, dataset_dir: str,
                     token_file: str | None = None) -> None:
    """
    Downloads a HuggingFace dataset from the HuggingFace Hub.
    :param dataset_name: The name of the dataset
    :param dataset_dir: The directory where the dataset should be stored
    :param token_file: Path to the file containing your HuggingFace token. If None,
        the dataset must be public.
    :return: None
    """
    if token_file is not None:
        huggingface_token = get_huggingface_token(token_file)
        login(token=huggingface_token)

    dataset = load_dataset(dataset_name)
    dataset.save_to_disk(dataset_dir)
    logging.info(f"Downloaded dataset '{dataset_name}' from the HuggingFace Hub.")
