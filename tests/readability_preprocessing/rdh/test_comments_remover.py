from pathlib import Path

from readability_preprocessing.utils.utils import load_code
from src.readability_preprocessing.rdh.comments_remover import remove_comments, \
    CommentsRemover, CommentsRemoverConfig
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR, \
    COMMENTS_REMOVED_DIR, METHODS_ORIGINAL_DIR


def test_remove_comments():
    comments_remover = CommentsRemover(config=CommentsRemoverConfig(probability=1))
    filename = "flink_AbstractStreamOperatorV2.java_snapshotState.java"
    code = load_code(EXTRACTED_DIR / "stratum0" / "methods" / filename)
    code_cr = comments_remover.remove_comments(code)

    expected_code = "@Override\n" \
    "public void snapshotState(StateSnapshotContext context) throws Exception {}"
    assert code_cr == expected_code


def test_remove_comments_2():
    comments_remover = CommentsRemover(config=CommentsRemoverConfig(probability=1))
    code = load_code(METHODS_ORIGINAL_DIR / "towards.java")
    code_cr = comments_remover.remove_comments(code)
    print(code_cr)


class TestExtractSampled(DirTest):

    def test_remove_comments_dir(self):
        remove_comments(input_dir=Path(METHODS_ORIGINAL_DIR),
                        output_dir=Path(self.output_dir),
                        probability=1)
