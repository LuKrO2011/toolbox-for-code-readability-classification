import logging
import random
from dataclasses import dataclass
from pathlib import Path

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
        self.arr = []
        self.comment = "//"
        self.esc = "\\"
        self.bcopen = "/*"
        self.bcclose = "*/"
        self.comcheck = True
        self.esccheck = True
        self.bccheck = True

    def remove_comments(self, code: str) -> str:
        """
        Removes comments from the given java code.
        :param code: The java code with comments.
        :return: The java code without comments.
        """
        # Remove block comments
        if self.bccheck and self.bcopen != '':
            output = self.remove_block_comments(code)
        else:
            output = code

        # Remove line comments
        if self.comcheck and self.comment != '':
            output = self.remove_line_comments(output)

        # Remove extra newlines
        output = output.replace('\n\n', '\n').lstrip('\n')
        output = output.strip('\n')

        self.arr = []
        return output

    def remove_line_comments(self, code: str) -> str:
        """
        Removes line comments from the given java code.
        :param code: The java code with comments.
        :return: The java code without line comments.
        """
        lines = code.split('\n')
        for line in lines:
            rem = self._remove_comments_from_line(line)
            if not rem.strip():
                rem = '\n'
            self.arr.append(rem)

        code = '\n'.join(self.arr)
        return code

    def _remove_comments_from_line(self, line: str) -> str:
        """
        Removes comments from a single line of java code.
        :param line: The line of java code with comments.
        :return: The line of java code without comments.
        """
        if self.esc == '':
            self.esc = None

        if self.comment in line:
            comment_indexes = [i for i in range(len(line)) if
                               line.startswith(self.comment, i)]
            if self._should_remove_comment():
                output = self._extract_comment_free_line(line, comment_indexes)
            else:
                output = line
        else:
            output = line

        return output

    def _extract_comment_free_line(self, line: str, comment_indexes: list) -> str:
        """
        Extracts the comment free line from the given line of java code.
        :param line: The line of java code with comments.
        :param comment_indexes: The indexes of the comments in the line.
        :return: The line of java code without comments.
        """
        d, s = 0, 0  # double and single quote counters
        rem = line

        i = 0
        while i < len(line):
            check = self._is_valid_quote(line, i)
            if line[i] == '"' and check and d == 0 and s == 0:
                d += 1
            elif line[i] == '"' and check and d == 1 and s == 0:
                d -= 1

            if line[i] == "'" and check and d == 0 and s == 0:
                s += 1
            elif line[i] == "'" and check and d == 0 and s == 1:
                s -= 1

            if i in comment_indexes and d == 0 and s == 0:
                rem = line[:i]
                break

            i += 1

        return rem

    def _is_valid_quote(self, line: str, i: int) -> bool:
        """
        Checks if the given quote is valid.
        :param i: The index of the quote in the line.
        :param line: The line of java code with comments.
        :return: True if the quote is valid, False otherwise.
        """
        if not self.esccheck or self.esc == '':
            return True
        esc_slice = line[i - len(self.esc):i]
        is_escaped = esc_slice == self.esc
        line_minus_escaped = line[i - 2 * len(self.esc):i - len(self.esc)]
        return not is_escaped or (is_escaped and line_minus_escaped == self.esc)

    def _find_block_comment_indexes(self, full: str) -> tuple:
        """
        Finds the indexes of the block comments in the given java code.
        :param full: The java code with comments.
        :return: The indexes of the block comments.
        """
        bc_open_indexes = []
        bc_close_indexes = []
        o, c = -1, -1
        while (o := full.find(self.bcopen, o + 1)) != -1:
            bc_open_indexes.append(o)
        if self.bcclose != '':
            while (c := full.find(self.bcclose, c + 1)) != -1:
                bc_close_indexes.append(c)
        return bc_open_indexes, bc_close_indexes

    def _check_quotes(self, i: int, full: str, bc_open_indexes: list,
                      bc_close_indexes: list, d: int, s: int) -> tuple:
        """
        Checks the double quotes and single quotes in the given java code.
        :param i: The index of the character in the java code.
        :param full: The java code with comments.
        :param bc_open_indexes: The indexes of the block comments in the java code.
        :param bc_close_indexes: The indexes of the block comments in the java code.
        :param d: The double quote counter.
        :param s: The single quote counter.
        :return: The updated double and single quote counters.
        """
        if full[i] == '"' and self._is_valid_double_quote(i, full, d, s):
            d += 1
        elif full[i] == '"' and self._is_valid_double_quote(i, full, d, s,
                                                            closing=True):
            d -= 1
        if full[i] == "'" and self._is_valid_single_quote(i, full, d, s,
                                                          bc_open_indexes):
            s += 1
        elif full[i] == "'" and self._is_valid_single_quote(i, full, d, s,
                                                            bc_close_indexes):
            s -= 1
        return d, s

    def _is_valid_double_quote(self, i: int, full: str, d: int, s: int,
                               closing=False) -> bool:
        """
        Checks if the given quote is valid.
        :param i: The index of the quote in the line.
        :param full: The line of java code with comments.
        :param d: The double quote counter.
        :param s: The single quote counter.
        :param closing: True if the quote is a closing quote, False otherwise.
        :return: True if the quote is valid, False otherwise.
        """
        return (
            full[i] == '"' and
            self._is_valid_quote(full, i)
        ) and d == 0 and s == 0 and (not closing or d == 1)

    def _is_valid_single_quote(self, i: int, full: str, d: int, s: int,
                               bc_indexes: list) -> bool:
        """
        Checks if the given single quote is valid.
        :param i: The index of the single quote in the line.
        :param full: The line of java code with comments.
        :param d: The double quote counter.
        :param s: The single quote counter.
        :param bc_indexes: The indexes of the block comments in the java code.
        :return: True if the single quote is valid, False otherwise.
        """
        return (
            full[i] == "'" and
            self._is_valid_quote(full, i)
        ) and d == 0 and s == 0 and (i not in bc_indexes)

    def remove_block_comments(self, full: str) -> str:
        """
        Removes block comments from the given java code.
        :param full: The java code with comments.
        :return: The java code without block comments.
        """
        output = ""
        bc_open_indexes, bc_close_indexes = self._find_block_comment_indexes(full)
        d, s, bc, record = 0, 0, 0, 0

        for i in range(len(full)):
            d, s = self._check_quotes(i, full, bc_open_indexes,
                                      bc_close_indexes, d, s)

            if full[i] == '\n':
                d = 0
                s = 0

            if i in bc_open_indexes and d == 0 and s == 0 and bc == 0:
                output += full[record:i]
                i += len(self.bcopen) - 1
                bc = 1
            elif self.bcclose != '' and i in bc_close_indexes and bc == 1:
                if self._should_remove_comment():
                    record = i + len(self.bcclose)
                    i += len(self.bcclose) - 1
                    bc = 0
                else:
                    index = bc_close_indexes.index(i)
                    bc_open_pos = bc_open_indexes[index]
                    output += full[bc_open_pos:i + len(self.bcclose)]
                    record = i + len(self.bcclose)
                    i += len(self.bcclose) - 1
                    bc = 0
            elif i == len(full) - 1 and bc == 0:
                output += full[record:]

        return output

    def _should_remove_comment(self) -> bool:
        """
        True if comments should be removed, False otherwise.
        :return: True if comments should be removed, False otherwise.
        """
        return random.random() < self.config.probability


def remove_comments(input_dir: Path, output_dir: Path,
                    probability: float = 0.1) -> None:
    """
    Removes comments from the java files in the input directory and stores the result
    in the output directory.
    :param input_dir: The input directory.
    :param output_dir: The output directory.
    :param probability: The probability of removing a comment.
    """
    comments_remover = CommentsRemover(
        CommentsRemoverConfig(
            probability=probability
        )
    )

    java_files = list_java_files_path(input_dir)
    for file in java_files:
        logging.info(f"Processing file: {file}")
        code = load_code(file)
        code = comments_remover.remove_comments(code)
        store_code(code, file, input_dir, output_dir)
