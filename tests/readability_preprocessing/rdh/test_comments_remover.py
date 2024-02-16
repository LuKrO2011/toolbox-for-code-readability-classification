from pathlib import Path

from readability_preprocessing.utils.utils import load_code
from src.readability_preprocessing.rdh.comments_remover import remove_comments, \
    CommentsRemover, CommentsRemoverConfig
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR, \
    METHODS_ORIGINAL_DIR


def test_remove_comments():
    comments_remover = CommentsRemover(config=CommentsRemoverConfig(probability=1))
    filename = "flink_AbstractStreamOperatorV2.java_snapshotState.java"
    code = load_code(EXTRACTED_DIR / "stratum0" / "methods" / filename)
    code_cr = comments_remover.remove_comments(code)

    expected_code = (
        "@Override\n"
        "public void snapshotState(StateSnapshotContext context) throws Exception {}"
    )
    assert code_cr == expected_code


def test_remove_comments_2():
    comments_remover = CommentsRemover(config=CommentsRemoverConfig(probability=1))
    code = load_code(METHODS_ORIGINAL_DIR / "towards.java")
    code_cr = comments_remover.remove_comments(code)

    expected_code = (
        "public void getNumber(){\n"
        "    int count = 0;\n"
        "    while(count < 10){\n"
        "        count++;\n"
        "    }\n"
        "}"
    )
    assert code_cr == expected_code


def test_remove_comments_3():
    comments_remover = CommentsRemover(config=CommentsRemoverConfig(probability=1))
    code = load_code(
        METHODS_ORIGINAL_DIR / "AreaShop" / "AddCommand.java" / "getCommandStart.java")
    code_cr = comments_remover.remove_comments(code)

    expected_code = (
        "\tpublic String getCommandStart() {\n"
        "\t\treturn \"areashop add\";\n"
        "\t}"
    )
    assert code_cr == expected_code


class TestExtractSampled(DirTest):

    def test_remove_comments_dir(self):
        remove_comments(input_dir=Path(METHODS_ORIGINAL_DIR),
                        output_dir=Path(self.output_dir),
                        probability=1)
