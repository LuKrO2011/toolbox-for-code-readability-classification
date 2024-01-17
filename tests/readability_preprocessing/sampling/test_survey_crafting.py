from pathlib import Path

from readability_preprocessing.sampling.survey_crafting import craft_surveys
from tests.readability_preprocessing.utils.utils import DirTest

input_dir = Path("C:/Users/lukas/IdeaProjects/rdh-stratas")


class TestSurveyCrafting(DirTest):

    def test_sample(self):
        craft_surveys(input_dir=input_dir, output_dir=self.output_dir,
                      snippets_per_sheet=4, num_sheets=4)
