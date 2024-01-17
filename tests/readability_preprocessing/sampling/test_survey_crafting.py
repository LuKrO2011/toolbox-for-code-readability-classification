from pathlib import Path

from readability_preprocessing.sampling.survey_crafting import craft_surveys
from readability_preprocessing.utils.utils import num_files
from tests.readability_preprocessing.utils.utils import DirTest, EXTRACTED_DIR

input_dir = Path("C:/Users/lukas/IdeaProjects/rdh-stratas")


class TestSurveyCrafting(DirTest):

    def test_sample(self):
        craft_surveys(input_dir=EXTRACTED_DIR, output_dir=self.output_dir,
                      snippets_per_sheet=2, num_sheets=2)

        # Check that the output directory contains the correct number of files
        num_files_output = num_files(self.output_dir)
        assert num_files_output == 4
        num_files_sheet_0 = num_files(self.output_dir + "/sheet_0")
        assert num_files_sheet_0 == 2
        num_files_sheet_1 = num_files(self.output_dir + "/sheet_1")
        assert num_files_sheet_1 == 2

    def test_sample_too_many_snippets(self):
        craft_surveys(input_dir=EXTRACTED_DIR, output_dir=self.output_dir,
                      snippets_per_sheet=10, num_sheets=2)

        # Check that the output directory contains the correct number of files
        num_files_input = num_files(EXTRACTED_DIR)
        num_files_output = num_files(self.output_dir + "/sheet_0")
        assert num_files_output == num_files_input


