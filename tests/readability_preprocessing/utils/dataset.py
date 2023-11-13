import os
from tempfile import TemporaryDirectory

from datasets import load_from_disk

from src.readability_preprocessing.utils.dataset import \
    generate_java_files_from_dataset, \
    add_images_to_dataset

RES_DIR = os.path.join(os.path.dirname(__file__), "../../res/")
DATASET_DIR = RES_DIR + "datasets/"
RAW_DATASET_DIR = DATASET_DIR + "raw/"
WITH_IMAGES_DATASET_DIR = DATASET_DIR + "with_images/"
IMAGES_DIR = RES_DIR + "images/"


def test_generate_java_files_from_dataset():
    name = "bw"
    dataset_dir = RAW_DATASET_DIR + name

    # Create temporary directory
    temp_dir = TemporaryDirectory()

    # Load the dataset
    dataset = load_from_disk(dataset_dir)

    # Generate the Java files
    generate_java_files_from_dataset(dataset_dir, temp_dir.name)

    # Check that 100 java files were generated
    assert len(os.listdir(temp_dir.name)) == len(dataset)
    for file in os.listdir(temp_dir.name):
        assert file.endswith(".java")

    # Clean up temporary directories
    temp_dir.cleanup()


def test_add_images_to_dataset():
    name = "bw"
    dataset_dir = RAW_DATASET_DIR + name
    images_dir = IMAGES_DIR + name
    dataset_with_images_dir = WITH_IMAGES_DATASET_DIR + name

    # Create temporary directory
    temp_dir = TemporaryDirectory()

    # Add the images to the dataset
    add_images_to_dataset(images_dir, dataset_dir, temp_dir.name)

    # Load the new dataset
    dataset = load_from_disk(temp_dir.name)

    # Check that the dataset contains the images
    for data in dataset:
        assert "image" in data

    # Check that the images from the dataset match the images in the images dir
    for idx, data in enumerate(dataset):
        image = data["image"]
        with open(os.path.join(images_dir, f"{idx}.java.png"), "rb") as f:
            assert image == f.read()

    # Check that the dataset is the same as the "with images" dataset
    dataset_with_images = load_from_disk(dataset_with_images_dir)
    for data, data_with_images in zip(dataset, dataset_with_images):
        assert data == data_with_images

    # Clean up temporary directories
    temp_dir.cleanup()
