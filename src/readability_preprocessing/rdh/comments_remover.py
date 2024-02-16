from dataclasses import dataclass

import re
import random
from pathlib import Path

from readability_preprocessing.utils.utils import list_java_files_path, \
    load_code, store_code

COMMENT_PATTERN = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
COMMENT_REGEX = re.compile(COMMENT_PATTERN, re.MULTILINE | re.DOTALL)


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

        def remove_comment(match: re.Match) -> str:
            """
            Removes the comment with the given probability.
            :param match: The match object.
            :return: The comment or an empty string.
            """
            return '' if random.random() < self.config.probability else match.group(0)

        # Use regex to replace comments with an empty string with the given probability
        code_without_comments = COMMENT_REGEX.sub(remove_comment, code)

        # Remove empty line at the beginning or end of the file
        code_without_comments = code_without_comments.strip()

        return code_without_comments


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
