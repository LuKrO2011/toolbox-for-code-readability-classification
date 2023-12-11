import os

from src.readability_preprocessing.extractors.file_extractor import extract_files
from tests.readability_preprocessing.utils.utils import DirTest, CHECKSTYLED_DIR


class TestExtractFiles(DirTest):

    def test_extract_files(self):
        extract_files(CHECKSTYLED_DIR.absolute(), self.output_dir)

        # DirWithNoNonViolatedFiles/Folder is not copied
        assert len(os.listdir(self.output_dir)) == 1

        # AreaShop is copied
        assert "AreaShop" in os.listdir(self.output_dir)
        area_shop_dir = os.path.join(self.output_dir, "AreaShop")
        assert "AddCommand.java" in os.listdir(area_shop_dir)
        assert "AreaShopInterface.java" in os.listdir(area_shop_dir)
