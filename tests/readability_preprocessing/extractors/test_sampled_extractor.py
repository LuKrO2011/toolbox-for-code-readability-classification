from pathlib import Path

from readability_preprocessing.extractors.sampled_extractor import extract_sampled
from tests.readability_preprocessing.utils.utils import DirTest, SAMPLED_DIR_2_2, \
    CODE_SNIPPETS_DIR


class TestExtractSampled(DirTest):

    def test_extract_sampled(self):
        extract_sampled(input_dirs=[Path(CODE_SNIPPETS_DIR)],
                        output_dir=Path(self.output_dir),
                        sampling_dir=Path(SAMPLED_DIR_2_2))

