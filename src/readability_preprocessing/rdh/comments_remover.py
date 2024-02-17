import random
from dataclasses import dataclass
from pathlib import Path

from pyparsing import ParseException, javaStyleComment

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
        comment_positions = []
        try:
            comments = javaStyleComment.scanString(code)
            for comment, start, end in comments:
                is_safe = self._quote_ends_before_comment(code, start)
                if is_safe:
                    comment_positions.append((start, end))
        except ParseException as pe:
            print(f"Error parsing input: {pe}")

        # Remove the comments from the code
        code = self._remove_comments_from_code(code, comment_positions)

        return code

    def _remove_comments_from_code(self, code: str, comment_positions: list) -> str:
        """
        Removes comments from the code at the given positions.
        :param code: The code.
        :param comment_positions: The positions of the comments.
        :return: The code without comments.
        """
        if len(comment_positions) == 0:
            return code

        # Sort the comment positions in reverse order
        comment_positions = sorted(comment_positions, key=lambda x: x[0], reverse=True)

        # Keep the comments with the given probability
        for start, end in comment_positions:
            if self._to_remove_comment():
                code = self._remove_comment(code, (start, end))
            else:
                code = self._keep_comment(code, (start, end))

        return code

    @staticmethod
    def _keep_comment(code: str, comment_position: tuple) -> str:
        """
        Keeps the comment from the code at the given position.
        :param code: The code.
        :param comment_position: The position of the comment.
        :return: The code with the comment.
        """
        return code

    @staticmethod
    def _remove_comment(code: str, comment_position: tuple) -> str:
        """
        Removes the comment from the code at the given position.
        :param code: The code.
        :param comment_position: The position of the comment.
        :return: The code without the comment.
        """
        start, end = comment_position
        return code[:start] + code[end:]

    def _to_remove_comment(self):
        """
        Returns True with the given probability.
        :return: True with the given probability.
        """
        return random.random() < self.config.probability

    @staticmethod
    def _quote_ends_before_comment(code: str, start: int) -> bool:
        """
        Returns True if the last quote before the comment is not closed.
        :param code: The code.
        :param start: The start of the comment.
        :return: True if the last quote before the comment is not closed.
        """
        code_before_comment = code[:start]
        quotes_count = code_before_comment.count('"') + code_before_comment.count('\'')
        return quotes_count % 2 == 0


def remove_comments(input_dir: Path, output_dir: Path,
                    probability: float = 0.1) -> None:
    """

    Removes
    comments
    with the given probability from the files in the input directory
    and saves
    the
    files in the
    output
    directory.
    :param
    input_dir: The
    input
    directory.
    :param
    output_dir: The
    output
    directory.
    :param
    probability: The
    probability
    of
    removing
    comments.
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
