from readability_preprocessing.sampling.diff_extractor import compare_java_files
from tests.readability_preprocessing.utils.utils import DIFF_EXTRACTOR_DIR


class TestCompareJavaFiles:

    def test_same_file(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "default.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_additionalTab(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "additionalTab.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is True

    def test_differentCharSet(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "differentCharSet.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_newlineAtTheEnd(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "newlineAtTheEnd.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False

    def test_whitespaceAtBeginningOfLine(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "whitespaceAtBeginningOfLine.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is True

    def test_whitespaceAtEndOfLine(self):
        file1_path = DIFF_EXTRACTOR_DIR / "default.java"
        file2_path = DIFF_EXTRACTOR_DIR / "whitespaceAtEndOfLine.java"

        has_diff = compare_java_files(file1_path, file2_path)
        assert has_diff is False
