import logging
import os
import random
import sys
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any, List

from readability_preprocessing.sampling.stratified_sampling import sample

DEFAULT_LOG_FILE_NAME = "readability-preprocessing"
DEFAULT_LOG_FILE = f"{DEFAULT_LOG_FILE_NAME}.log"


def _setup_logging(log_file: str = DEFAULT_LOG_FILE, overwrite: bool = False) -> None:
    """
    Set up logging.
    """
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


def store_as_txt(stratas: List[List[str]], output_dir: str) -> None:
    """
    Store the sampled Java code snippet paths in a txt file.
    :param stratas: The sampled Java code snippet paths
    :param output_dir: The directory where the txt file should be stored
    :return: None
    """
    with open(os.path.join(output_dir, "stratas.txt"), "w") as file:
        for stratum in stratas:
            file.write(f"Stratum {stratas.index(stratum)}:\n")
            for snippet in stratum:
                file.write(f"{snippet}\n")


class TaskNotSupportedException(Exception):
    """
    Exception is thrown whenever a task is not supported.
    """


class Tasks(Enum):
    """
    Enum for the different tasks of the readability preprocessing toolbox.
    """
    SAMPLE = "SAMPLE"

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
        help="Path to the folder containing java files to sample from.",
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

    # Get the paths to the Java code snippets
    stratas = sample(input_dir, output_dir=save_dir,
                     num_stratas=num_stratas,
                     snippets_per_stratum=snippets_per_stratum)

    # Log the results
    logging.info(f"The following Java code snippets were sampled:")
    for i, stratum in enumerate(stratas):
        for j, snippet_path in enumerate(stratum):
            logging.info(f"Stratum {i}, Snippet {j}: {snippet_path}")

    # Save the sampled Java code snippet_path paths
    if save_dir is not None:
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

    # Save the sampled Java code snippet paths
    if save_dir is not None:
        store_as_txt(stratas, save_dir)


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
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
