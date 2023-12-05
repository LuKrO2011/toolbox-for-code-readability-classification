import logging
import os

from datasets import load_from_disk, load_dataset
from huggingface_hub import login

from src.readability_preprocessing.utils.utils import image_to_bytes


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
