import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

import javalang
from javalang.parser import JavaSyntaxError
from javalang.tree import MethodDeclaration

# TODO: Fix Abstract methods of interfaces e.g. hadoop\AbfsCounter.java

INPUT_DIR = r"D:\PyCharm_Projects_D\styler2.0\extracted"
OUTPUT_DIR = r"D:\PyCharm_Projects_D\styler2.0\methods_2"


class OverwriteMode(Enum):
    """
    Enum for the overwrite mode of method extractor.
    """

    OVERWRITE = 0
    SKIP = 1


class MethodExtractorConfigurationError(Exception):
    """
    An exception class for MethodExtractor configuration errors.
    """

    def __init__(self, message: str):
        self.message = message


@dataclass
class MethodExtractorConfig:
    """
    A configuration class for the MethodExtractor.
    """

    def __init__(self, overwrite_mode: OverwriteMode, include_method_comments: bool,
                 comments_required: bool, remove_indentation: bool):
        self.overwrite_mode = overwrite_mode
        self.include_method_comments = include_method_comments
        self.comments_required = comments_required
        self.remove_indentation = remove_indentation


class MethodExtractor:
    """
    A class for extracting methods from java files.
    """

    def __init__(self, config: MethodExtractorConfig):
        self.config = config

        # Don't allow comments_required to be True if include_method_comments is False
        if self.config.comments_required and not self.config.include_method_comments:
            raise MethodExtractorConfigurationError(
                "include_method_comments must be True if comments_required is True."
            )

    def extract_methods_from_dir(self, input_dir: str, output_dir: str) -> None:
        """
        Extracts java methods from their classes and stores each in a separate file.
        :param input_dir: The input directory.
        :param output_dir: The output directory.
        :return: None.
        """
        # Check if the input directory exists and is a directory
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            logging.error(
                "Input directory %s does not exist or is not a directory.", input_dir
            )
            return

        # Iterate over each file_or_dir in the input directory
        for file_or_dir in os.listdir(input_dir):
            file_or_dir = os.path.join(input_dir, file_or_dir)
            # Check if the file_or_dir is a file_or_dir
            if os.path.isfile(file_or_dir):
                # Check if the file_or_dir is a java file_or_dir
                if file_or_dir.endswith(".java"):
                    self.extract_methods_from_file(file_or_dir, output_dir)
                else:
                    logging.warning("File %s is not a java file_or_dir.", file_or_dir)
            else:
                # Check if the file_or_dir is a directory
                if os.path.isdir(file_or_dir):
                    self.extract_methods_from_dir(file_or_dir, output_dir)

    def extract_methods_from_file(
        self,
        input_file: str,
        output_dir: str
    ) -> None:
        """
        Extracts java methods from a file and stores each in a separate file.
        :param input_file: The input file.
        :param output_dir: The output directory.
        :return: None.
        """
        # Check if the input file exists and is a file
        if not os.path.exists(input_file) or not os.path.isfile(input_file):
            logging.error("Input file %s does not exist or is not a file.", input_file)
            return

        # Specify the output subdirectory path and name
        output_subdir = os.path.join(output_dir, os.path.basename(input_file))

        # Check if we skip the file
        if (os.path.exists(
            output_subdir) and self.config.overwrite_mode == OverwriteMode.SKIP):
            logging.info(
                "Skipping file %s, because the output directory %s already exists.",
                input_file,
                output_dir,
            )
            return

        # Extract the methods from the source code
        methods = self._iterate_methods(input_file)
        logging.info("Found %d methods in file %s.", len(methods), input_file)

        # Create a subfolder for each input file if methods were found
        if methods:
            os.makedirs(output_subdir, exist_ok=True)

        # Write each method to a separate file
        for method_name, method_code in methods.items():
            output_file = os.path.join(output_subdir, method_name + ".java")
            with open(output_file, "w") as w:
                w.write(method_code)

    def _iterate_methods(self, file: str) -> dict[str, str]:
        """
        Iterates over the methods in a file and returns a dictionary containing the method
        name and the method code.
        :param file: The file.
        :return: A dictionary containing the method name and the method code.
        """
        # Check if the file exists and is a java file
        if not os.path.exists(file) or not file.endswith(".java"):
            logging.error("File %s does not exist or is not a java file.", file)
            return {}

        # Read the file
        try:
            with open(file) as r:
                codelines = r.readlines()
                code_text = "".join(codelines)
        except UnicodeDecodeError as e:
            logging.warning("Could not read file %s.", file)
            logging.warning(e)
            return {}

        methods = {}

        # Try to parse the file
        lex = None
        try:
            parse_tree = javalang.parse.parse(code_text)
        except JavaSyntaxError as e:
            logging.warning("Could not parse file %s: %s at %s", file, e.description,
                            e.at)
            logging.warning(e)
            return {}
        except Exception as e:
            logging.warning("Could not parse file %s.", file)
            logging.warning(e)
            return {}

        for _, method_node in parse_tree.filter(MethodDeclaration):
            startpos, endpos, startline, endline = self._get_method_start_end(
                parse_tree, method_node
            )
            method_text, startline, endline, lex = self._get_method_text(
                codelines, startpos, endpos, startline, endline
            )

            # Get the first line of the method text
            first_line = method_text.split("\n")[0].strip()

            # Check if COMMENTS_REQUIRED is True and the method has a comment
            if self.config.comments_required and not first_line.startswith("/"):
                logging.info(
                    "Skipping method %s, because it has no comment.", method_node.name
                )
                continue

            methods[method_node.name] = method_text

        return methods

    def _get_method_start_end(self,
                              parse_tree: list, method_node: MethodDeclaration
                              ) -> tuple[str, str, int, int]:
        """
        Get the start and end position of a method in the source code.
        :param parse_tree: The full parse tree.
        :param method_node: The method node.
        :return: The start and end position of the method.
        """
        startpos = None
        endpos = None
        startline = None
        endline = None

        # Iterate over the parse tree and find the method node
        for path, node in parse_tree:
            if startpos is not None and method_node not in path:
                endpos = node.position
                endline = node.position.line if node.position is not None else None
                break
            if startpos is None and node == method_node:
                startpos = node.position
                startline = node.position.line if node.position is not None else None
        return startpos, endpos, startline, endline

    def _get_method_text(self,
                         codelines: list[str],
                         startpos: str,
                         endpos: str,
                         startline: int,
                         endline: int,
                         include_method_comments: bool = True,
                         remove_indentation: bool = True,
                         ) -> tuple[str, int | None, int | None, Any]:
        """
        Get the text of a method, including any comments before the method.
        :param codelines: The code lines.
        :param startpos: The start position of the method.
        :param endpos: The end position of the method.
        :param startline: The start line of the method.
        :param endline: The end line of the method.
        :return: The text of the method.
        """
        if startpos is None:
            return "", None, None, None

        # Get the start and end line comment_index
        startline_index = startline - 1
        endline_index = endline - 1 if endpos is not None else None

        # Fetch the method code
        meth_text = "<ST>".join(codelines[startline_index:endline_index])
        meth_text = meth_text[: meth_text.rfind("}") + 1]

        # Remove trailing rbrace for last methods & any external content/comments
        # if endpos is None and
        if abs(meth_text.count("}") - meth_text.count("{")) != 0:
            # imbalanced braces
            brace_diff = abs(meth_text.count("}") - meth_text.count("{"))

            for _ in range(brace_diff):
                meth_text = meth_text[: meth_text.rfind("}")]
                meth_text = meth_text[: meth_text.rfind("}") + 1]

        # Remove any trailing comments within the method
        meth_lines = meth_text.split("<ST>")
        meth_text = "".join(meth_lines)
        last_endline_index = startline_index + (len(meth_lines) - 1)

        # Include comments before the method
        if last_endline_index is not None:
            comment_lines = []
            comment_index = startline_index - 1
            while comment_index >= 0 and (
                codelines[comment_index].strip().startswith("/")
                or codelines[comment_index].strip().startswith("*")
            ):
                comment_lines.insert(0, codelines[comment_index])
                comment_index -= 1

            comment_block = "".join(comment_lines)

            # Include comments block at the beginning of the method text
            if comment_block and include_method_comments:
                meth_text = comment_block + meth_text
                startline_index = comment_index + 1

        # Remove indentation from the method text
        if remove_indentation:
            meth_text = self._remove_indentation(meth_text)

        return (
            meth_text,
            (startline_index + 1),
            (last_endline_index + 1),
            last_endline_index,
        )

    def _remove_indentation(self, meth_text: str) -> str:
        """
        Remove indentation from the method text there is the same amount of indentation
        on each line.
        :param meth_text: The method text.
        :return: The method text without indentation.
        """
        meth_lines = meth_text.split("\n")
        indentation_changed = False
        minimal_indentation = len(meth_lines[0]) - len(meth_lines[0].lstrip())

        # Calculate the indentation of all lines
        for line in meth_lines:
            # Skip empty lines
            if not line.strip():
                continue

            indentation = len(line) - len(line.lstrip())

            if indentation < minimal_indentation:
                indentation_changed = True
                break

            minimal_indentation = min(indentation, minimal_indentation)

        # If the indentation is the same on each line, remove it
        if not indentation_changed:
            indentation = minimal_indentation
            for i, line in enumerate(meth_lines):
                meth_lines[i] = line[indentation:]

        return "\n".join(meth_lines)


def extract_methods(input_dir: str, output_dir: str,
                    overwrite_mode: OverwriteMode = OverwriteMode.OVERWRITE,
                    include_method_comments: bool = True,
                    comments_required: bool = True,
                    remove_indentation: bool = True) -> None:
    """
    Extracts java methods from their classes and stores each in a separate file.
    :param input_dir: The input directory.
    :param output_dir: The output directory.
    :param overwrite_mode: The overwrite mode.
    :param include_method_comments: Whether to include comments before the method.
    :param comments_required: Whether comments are required.
    :param remove_indentation: Whether to remove indentation.
    :return: None.
    """
    method_extractor = MethodExtractor(
        MethodExtractorConfig(
            overwrite_mode=overwrite_mode,
            include_method_comments=include_method_comments,
            comments_required=comments_required,
            remove_indentation=remove_indentation
        )
    )

    # Iterate over each directory in the input directory
    for directory in os.listdir(input_dir):
        if not os.path.isdir(os.path.join(input_dir, directory)):
            continue

        # Create a subfolder for each directory in the output directory
        output_subdir = os.path.join(output_dir, directory)
        method_extractor.extract_methods_from_dir(os.path.join(input_dir, directory),
                                                  output_subdir)


if __name__ == "__main__":
    extract_methods(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR)
