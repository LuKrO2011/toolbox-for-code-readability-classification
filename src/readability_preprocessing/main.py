import logging
import os
import random
import sys
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any

from readability_preprocessing.extractors.sampled_extractor import extract_sampled
from src.readability_preprocessing.dataset.dataset_combiner import combine_datasets
from src.readability_preprocessing.dataset.dataset_converter import convert_dataset_csv, \
    convert_dataset_two_folders, DatasetType
from src.readability_preprocessing.extractors.file_extractor import extract_files
from src.readability_preprocessing.extractors.method_extractor import extract_methods, \
    OverwriteMode
from src.readability_preprocessing.sampling.stratified_sampling import \
    calculate_features, StratifiedSampler
from src.readability_preprocessing.utils.csv import load_features_from_csv
from src.readability_preprocessing.utils.dataset import upload_dataset, \
    download_dataset

DEFAULT_LOG_FILE_NAME = "readability-preprocessing"
DEFAULT_LOG_FILE = f"{DEFAULT_LOG_FILE_NAME}.log"
DEFAULT_IMAGE_DIR_NAME = "images"
DEFAULT_CODE_DIR_NAME = "code"
DEFAULT_OUTPUT_DATASET_DIR_NAME = "dataset"


def _setup_logging(log_file: str = DEFAULT_LOG_FILE, overwrite: bool = False) -> None:
    """
    Set up logging.
    """
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
    EXTRACT_SAMPLED = "EXTRACT_SAMPLED"
    EXTRACT_FILES = "EXTRACT_FILES"
    EXTRACT_METHODS = "EXTRACT_METHODS"
    CONVERT_CSV = "CONVERT_CSV"
    CONVERT_TWO_FOLDERS = "CONVERT_TWO_FOLDERS"
    COMBINE = "COMBINE"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        raise TaskNotSupportedException(f"{value} is a not supported Task!")

    def __str__(self) -> str:
        return self.value


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

    # Parser for the extraction of sampled files
    extract_sampled_parser = sub_parser.add_parser(str(Tasks.EXTRACT_SAMPLED))
    extract_sampled_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        nargs="+",
        help="Path to the folders containing the extracted methods.",
    )
    extract_sampled_parser.add_argument(
        "--sampling",
        "-s",
        required=True,
        type=str,
        help="Path to the folder containing the sampling information (from SAMPLE).",
    )
    extract_sampled_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the sampled, extracted methods should be stored.",
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

    # Parser for converting csv datasets
    convert_csv_parser = sub_parser.add_parser(str(Tasks.CONVERT_CSV))
    convert_csv_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the folder containing the java files.",
    )
    convert_csv_parser.add_argument(
        "--csv",
        "-c",
        required=True,
        type=Path,
        help="Path to the csv file containing the ratings.",
    )
    convert_csv_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Path to the folder where the converted dataset should be stored.",
    )
    convert_csv_parser.add_argument(
        "--dataset-type",
        "-dt",
        required=True,
        type=str,
        choices=[dataset_type.value for dataset_type in DatasetType],
        help="The type of the dataset.",
    )

    # Parser for converting two folder datasets
    convert_two_folders_parser = sub_parser.add_parser(str(Tasks.CONVERT_TWO_FOLDERS))
    convert_two_folders_parser.add_argument(
        "--readable",
        "-r",
        required=True,
        type=str,
        help="Path to the folder containing the readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--not-readable",
        "-nr",
        required=True,
        type=str,
        help="Path to the folder containing the not readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the converted dataset should be stored.",
    )
    convert_two_folders_parser.add_argument(
        "--readable-score",
        "-rs",
        required=False,
        type=float,
        default=4.5,
        help="The readability score of the readable java files.",
    )
    convert_two_folders_parser.add_argument(
        "--not-readable-score",
        "-nrs",
        required=False,
        type=float,
        default=1.5,
        help="The readability score of the not readable java files.",
    )

    # Parser for combining datasets
    combine_parser = sub_parser.add_parser(str(Tasks.COMBINE))
    combine_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        nargs="+",
        help="Paths to the folders containing the datasets.",
    )
    combine_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the combined dataset should be stored.",
    )
    combine_parser.add_argument(
        "--percent-to-remove",
        "-ptr",
        required=False,
        type=float,
        default=0.5,
        help="Percentage of ambiguous samples to remove from the dataset.",
    )

    # Parser for uploading datasets
    upload_parser = sub_parser.add_parser(str(Tasks.UPLOAD))
    upload_parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to the folder containing the dataset.",
    )
    upload_parser.add_argument(
        "--name",
        "-n",
        required=True,
        type=str,
        help="Name of the dataset.",
    )
    upload_parser.add_argument(
        "--token-file",
        "-tf",
        required=True,
        type=str,
        help="Path to the file containing your HuggingFace token.",
    )

    # Parser for downloading datasets
    download_parser = sub_parser.add_parser(str(Tasks.DOWNLOAD))
    download_parser.add_argument(
        "--name",
        "-n",
        required=True,
        type=str,
        help="Name of the dataset.",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=str,
        help="Path to the folder where the dataset should be stored.",
    )
    download_parser.add_argument(
        "--token-file",
        "-tf",
        required=False,
        type=str,
        help="Path to the file containing your HuggingFace token. If not specified, "
             "the dataset must be public.",
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

    # Perform stratified sampling
    StratifiedSampler(save_dir=save_dir).sample(features=features,
                                                max_num_stratas=num_stratas,
                                                num_snippets=snippets_per_stratum)


def _run_extract_sampled(parsed_args: Any) -> None:
    """
    Extracts the sampled files from the input director(ies) as specified in the sampling
    information. Stores the extracted files in the output directory.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    # Get the parsed arguments
    input_dirs = parsed_args.input
    sampling_dir = parsed_args.sampling
    output_dir = parsed_args.output

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Extract the files
    extract_sampled(input_dirs=input_dirs, output_dir=output_dir,
                    sampling_dir=sampling_dir)


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


def _run_convert_csv(parsed_args: Any) -> None:
    """
    Converts a dataset from a folder of snippets and csv with ratings to a HuggingFace
    dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    snippets_dir = parsed_args.input
    csv = parsed_args.csv
    output_path = parsed_args.output
    dataset_type = DatasetType(parsed_args.dataset_type)

    convert_dataset_csv(snippets_dir=snippets_dir, csv=csv, output_path=output_path,
                        dataset_type=dataset_type)


def _run_convert_two_folders(parsed_args: Any) -> None:
    """
    Converts a dataset from two folders of snippets to a HuggingFace dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    readable_snippets_dir = parsed_args.readable
    readable_score = parsed_args.readable_score
    not_readable_snippets_dir = parsed_args.not_readable
    not_readable_score = parsed_args.not_readable_score
    output_path = parsed_args.output

    convert_dataset_two_folders(original=readable_snippets_dir,
                                rdh=not_readable_snippets_dir,
                                original_score=readable_score,
                                rdh_score=not_readable_score,
                                output_path=output_path)


def _run_combine_datasets(parsed_args: Any) -> None:
    """
    Converts a dataset to a HuggingFace dataset.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    input_paths = parsed_args.input
    output_dir = parsed_args.output
    percent_to_remove = parsed_args.percent_to_remove

    # Create the output directory, if it does not exist
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Convert the dataset
    combine_datasets(input_paths, output_dir, percent_to_remove)


def _run_download(parsed_args: Any) -> None:
    """
    Downloads a dataset from the HuggingFace hub.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    dataset_name = parsed_args.name
    dataset_dir = parsed_args.output
    token_file = parsed_args.token_file

    download_dataset(dataset_name=dataset_name,
                     dataset_dir=dataset_dir,
                     token_file=token_file)


def _run_upload(parsed_args: Any) -> None:
    """
    Uploads a dataset to the HuggingFace hub.
    :param parsed_args: Parsed arguments.
    :return: None
    """
    dataset_dir = parsed_args.input
    dataset_name = parsed_args.name
    token_file = parsed_args.token_file

    upload_dataset(dataset_dir=dataset_dir,
                   dataset_name=dataset_name,
                   token_file=token_file)


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
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
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
        case Tasks.EXTRACT_FILES:
            _run_extract_files(parsed_args)
        case Tasks.EXTRACT_METHODS:
            _run_extract_methods(parsed_args)
        case Tasks.CONVERT_CSV:
            _run_convert_csv(parsed_args)
        case Tasks.CONVERT_TWO_FOLDERS:
            _run_convert_two_folders(parsed_args)
        case Tasks.COMBINE:
            _run_combine_datasets(parsed_args)
        case Tasks.DOWNLOAD:
            _run_download(parsed_args)
        case Tasks.UPLOAD:
            _run_upload(parsed_args)

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
