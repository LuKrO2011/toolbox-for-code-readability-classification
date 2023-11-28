import logging
import os
import random
import sys
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any

from pyarrow.fs import copy_files

from readability_preprocessing.extractors.file_extractor import extract_files
from readability_preprocessing.extractors.method_extractor import extract_methods
from readability_preprocessing.preprocessing.visual import code_to_image
from readability_preprocessing.sampling.stratified_sampling import sample, \
    calculate_features
from readability_preprocessing.utils.csv import load_features_from_csv
from readability_preprocessing.utils.dataset import add_images_to_dataset, \
    is_huggingface_dataset, generate_java_files_from_dataset
from readability_preprocessing.utils.utils import store_as_txt, list_java_files

DEFAULT_LOG_FILE_NAME = "readability-preprocessing"
DEFAULT_LOG_FILE = f"{DEFAULT_LOG_FILE_NAME}.log"
DEFAULT_IMAGE_DIR_NAME = "images"
DEFAULT_CODE_DIR_NAME = "code"
DEFAULT_OUTPUT_DATASET_DIR_NAME = "dataset"


def _setup_logging(log_file: str = DEFAULT_LOG_FILE, overwrite: bool = False) -> None:
    """
    Set up logging.
    """
    # Create the log file and dir if it does not exist
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")

    # Get the overwrite flag
    mode = "w" if overwrite else "a"

    # Set the logging level
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)

    # Create a file handler to write messages to a log file
    file_handler = logging.FileHandler(log_file, mode=mode)
    file_handler.setLevel(logging_level)

    # Create a console handler to display messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)

    # Define the log format
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Get the root logger and add the handlers
    logger = logging.getLogger("")
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class TaskNotSupportedException(Exception):
    """
    Exception is thrown whenever a task is not supported.
    """


class Tasks(Enum):
    """
    Enum for the different tasks of the readability preprocessing toolbox.
    """
    SAMPLE = "SAMPLE"
    VISUALIZE = "VISUALIZE"
    EXTRACT_FILES = "EXTRACT_FILES"
    EXTRACT_METHODS = "EXTRACT_METHODS"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise TaskNotSupportedException(f"{value} is a not supported Task!")

    def __str__(self) -> str:
        return self.value


class OverwriteMode(Enum):
    """
    Enum for the overwrite mode of method extractor.
    """

    OVERWRITE = 0
    SKIP = 1


def _set_up_arg_parser() -> ArgumentParser:
    """
    Parses the arguments for the readability classifier.
    :return_:   Returns the parser for extracting the arguments.
    """
    arg_parser = ArgumentParser()
    sub_parser = arg_parser.add_subparsers(dest="command", required=True)

    # Parser for the sampling task
    sample_parser = sub_parser.add_parser(str(Tasks.SAMPLE))
    sample_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing java files to sample from or to a csv file "
             "containing the paths and features of the java files.",
    )
    sample_parser.add_argument(
        "--save",
        "-s",
        required=False,
        type=Path,
        help="Path to the folder where the intermediate results and the final sampling "
             "result should be stored. If not specified, the results are not stored.",
    )
    sample_parser.add_argument(
        "--num-stratas",
        "-n",
        required=False,
        type=int,
        default=20,
        help="Number of stratas to use for sampling.",
    )
    sample_parser.add_argument(
        "--snippets-per-stratum",
        "-sps",
        required=False,
        type=int,
        default=20,
        help="Number of snippets to sample per stratum.",
    )

    # Parser for generating visualisations
    visualize_parser = sub_parser.add_parser(str(Tasks.VISUALIZE))
    visualize_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing java files, a single java file or a folder "
             "with a HuggingFace dataset.",
    )
    visualize_parser.add_argument(
        "--save",
        "-s",
        required=True,
        type=Path,
        help="Path to the folder where the visualisations should be stored."
    )
    visualize_parser.add_argument(
        "--css",
        required=False,
        type=Path,
        help="Path to the css file to use for styling the code.",
        default=os.path.join(os.path.dirname(__file__), "../res/css/towards.css")
    )
    visualize_parser.add_argument(
        "--width",
        required=False,
        type=int,
        default=128,
        help="Width of the image.",
    )
    visualize_parser.add_argument(
        "--height",
        required=False,
        type=int,
        default=128,
        help="Height of the image.",
    )

    # Parser for extracting files
    extract_files_parser = sub_parser.add_parser(str(Tasks.EXTRACT_FILES))
    extract_files_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the processed projects.",
    )
    extract_files_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the files should be stored.",
    )
    extract_files_parser.add_argument(
        "--non-violated-subdir",
        "-nvs",
        required=False,
        type=str,
        default="non_violated",
        help="Name of the subdirectory containing the non-violated files.",
    )

    # Parser for extracting methods
    extract_methods_parser = sub_parser.add_parser(str(Tasks.EXTRACT_METHODS))
    extract_methods_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the processed projects.",
    )
    extract_methods_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the methods should be stored.",
    )
    extract_methods_parser.add_argument(
        "--overwrite-mode",
        "-om",
        required=False,
        type=OverwriteMode,
        choices=list(OverwriteMode),
        default=OverwriteMode.SKIP,
        help="Overwrite mode for the method extraction.",
    )
    extract_methods_parser.add_argument(
        "--include-method-comments",
        "-imc",
        required=False,
        type=bool,
        default=True,
        help="Whether to include the comments of the method.",
    )
    extract_methods_parser.add_argument(
        "--comments-required",
        "-cr",
        required=False,
        type=bool,
        default=True,
        help="Whether to only extract methods with comments.",
    )
    extract_methods_parser.add_argument(
        "--remove-indentation",
        "-ri",
        required=False,
        type=bool,
        default=True,
        help="Whether to remove the indentation of the code.",
    )

    return arg_parser


def _run_stratified_sampling(args: Any) -> None:
    """
    Perform stratified sampling on a list of Java code snippets.
    :return: None
    """
    # Get the input and output paths
    input_dir = args.input
    save_dir = args.save
    num_stratas = args.num_stratas
    snippets_per_stratum = args.snippets_per_stratum

    # Create the save directory, if it does not exist
    if save_dir is not None:
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

    # If the input is a csv file, read the paths and features from the csv file
    if input_dir.suffix == ".csv":
        features = load_features_from_csv(input_dir)
    else:  # If the input is a directory, get the paths to the Java code snippets
        features = calculate_features(input_dir, save_dir)

    # Get the paths to the Java code snippets
    stratas = sample(features,
                     num_stratas=num_stratas,
                     snippets_per_stratum=snippets_per_stratum)

    # Log the results
    logging.info(f"The following Java code snippets were sampled:")
    for i, stratum in enumerate(stratas):
        for j, snippet_path in enumerate(stratum):
            logging.info(f"Stratum {i}, Snippet {j}: {snippet_path}")

    # Save the sampled Java code snippet paths
    if save_dir is not None:
        store_as_txt(stratas, save_dir)


def _run_visualize(parsed_args: Any, image_dir_name=DEFAULT_IMAGE_DIR_NAME,
                   code_dir_name=DEFAULT_CODE_DIR_NAME,
                   output_dataset_dir_name=DEFAULT_OUTPUT_DATASET_DIR_NAME) -> None:
    """
    Runs the visualization of Java snippets.
    :param parsed_args: Parsed arguments.
    :param image_dir_name: The name of the image directory.
    :param code_dir_name: The name of the code directory.
    :param output_dataset_dir_name: The name of the output dataset directory.
    :return: None
    """
    # Get the parsed arguments
    input_dir = parsed_args.input
    save_dir = parsed_args.save
    css = parsed_args.css
    width = parsed_args.width
    height = parsed_args.height

    # Create the save directory, if it does not exist
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Create the image directory, if it does not exist
    image_dir = os.path.join(save_dir, image_dir_name)
    if not os.path.isdir(image_dir):
        os.makedirs(image_dir)

    # Create the code directory, if it does not exist
    code_dir = os.path.join(save_dir, code_dir_name)
    if not os.path.isdir(code_dir):
        os.makedirs(code_dir)

    # Create the output dataset directory, if it does not exist
    output_dataset_dir = None
    if is_huggingface_dataset(input_dir):
        output_dataset_dir = os.path.join(save_dir, output_dataset_dir_name)
        if not os.path.isdir(output_dataset_dir):
            os.makedirs(output_dataset_dir)

    # Get the paths to the Java snippets
    if input_dir.is_dir():
        if is_huggingface_dataset(input_dir):
            generate_java_files_from_dataset(input_dir, code_dir)
            java_code_snippet_paths = list_java_files(code_dir)
        else:
            copy_files(input_dir, code_dir)
            java_code_snippet_paths = list_java_files(input_dir)
    else:
        java_code_snippet_paths = [input_dir]

    # Create the visualisations
    for snippet_path in java_code_snippet_paths:
        code = open(snippet_path, "r").read()
        name = os.path.join(image_dir, os.path.basename(snippet_path) + ".png")
        code_to_image(code, output=name, css=css, width=width, height=height)
        logging.info(f"Visualized {snippet_path}.")

    logging.info(f"Visualized {len(java_code_snippet_paths)} Java code snippets.")

    # Store the visualisations as a HuggingFace dataset
    if is_huggingface_dataset(input_dir):
        add_images_to_dataset(image_dir, input_dir, output_dataset_dir)


def _run_extract_files(parsed_args: Any) -> None:
    """
    Extracts successfully processed files from the input directory.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    non_violated_subdir = parsed_args.non_violated_subdir

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Extract the files
    extract_files(input_dir=input_dir, output_dir=output_dir,
                  non_violated=non_violated_subdir)


def _run_extract_methods(parsed_args: Any) -> None:
    """
    Extracts java methods from their classes and stores each in a separate file.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dir = parsed_args.input
    output_dir = parsed_args.output
    overwrite_mode = parsed_args.overwrite_mode
    include_method_comments = parsed_args.include_method_comments
    comments_required = parsed_args.comments_required
    remove_indentation = parsed_args.remove_indentation

    os.makedirs(output_dir, exist_ok=True)

    # Extract the methods
    extract_methods(input_dir=input_dir, output_dir=output_dir,
                    overwrite_mode=overwrite_mode,
                    include_method_comments=include_method_comments,
                    comments_required=comments_required,
                    remove_indentation=remove_indentation)


def main(args: list[str]) -> int:
    """
    Main function of the readability classifier.
    :param args:  List of arguments.
    :return:    Returns 0 if the program was executed successfully.
    """
    arg_parser = _set_up_arg_parser()
    parsed_args = arg_parser.parse_args(args)
    task = Tasks(parsed_args.command)

    # Set up logging and specify logfile name
    logfile = DEFAULT_LOG_FILE
    if hasattr(parsed_args, "save") and parsed_args.save:
        folder_path = Path(parsed_args.save)
        folder_name = Path(parsed_args.save).name
        logfile = folder_path / Path(f"{DEFAULT_LOG_FILE_NAME}-{folder_name}.log")
    _setup_logging(logfile, overwrite=True)

    # Set a random seed
    random.seed(42)
    logging.info(f"Seed: {42}")

    # Execute the task
    match task:
        case Tasks.SAMPLE:
            _run_stratified_sampling(parsed_args)
        case Tasks.VISUALIZE:
            _run_visualize(parsed_args)
        case Tasks.EXTRACT_FILES:
            _run_extract_files(parsed_args)
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
