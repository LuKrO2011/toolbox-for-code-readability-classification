from dataclasses import dataclass
from pathlib import Path

import pyparsing
import pyparsing as pp

from readability_preprocessing.utils.utils import list_java_files_path, \
    load_code, store_code


@dataclass
class CommentsRemoverConfig:
    """
    A configuration class for the CommentsRemover.
    """

    def __init__(self, probability: float = 0.1):
        self.probability = probability


class CommentsRemover:
    """
    A class for removing comments from files with java methods.
    """

    def __init__(self, config: CommentsRemoverConfig):
        self.config = config

    def remove_comments(self, code: str) -> str:
        """
        Removes comments from the given code with the given probability.
        The comments can be javadoc, block or line comments.
        :param code: The code to remove comments from.
        :return: The code without comments.
        """
        comments = pyparsing.javaStyleComment
        output = comments.transform_string(code).suppress()

        # Strip newlines at the beginning and end of the output
        output = output.strip("\n")

        return output


def remove_comments(input_dir: Path, output_dir: Path,
                    probability: float = 0.1) -> None:
    """
    Removes comments with the given probability from the files in the input directory
    and saves the files in the output directory.
    :param input_dir: The input directory.
    :param output_dir: The output directory.
    :param probability: The probability of removing comments.
    :return: None.
    """
    comments_remover = CommentsRemover(
        CommentsRemoverConfig(
            probability=probability
        )
    )

    java_files = list_java_files_path(input_dir)
    for file in java_files:
        code = load_code(file)
        code = comments_remover.remove_comments(code)
        store_code(code, file, input_dir, output_dir)
