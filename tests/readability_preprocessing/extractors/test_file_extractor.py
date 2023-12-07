import os

from src.readability_preprocessing.extractors.file_extractor import extract_files
from tests.readability_preprocessing.utils.utils import DirTest, CHECKSTYLED_DIR


class TestExtractFiles(DirTest):

    def test_extract_files(self):
        extract_files(CHECKSTYLED_DIR.absolute(), self.temp_dir.name)

        # DirWithNoNonViolatedFiles/Folder is not copied
        assert len(os.listdir(self.temp_dir.name)) == 1

        # AreaShop is copied
        assert "AreaShop" in os.listdir(self.temp_dir.name)
        area_shop_dir = os.path.join(self.temp_dir.name, "AreaShop")
        assert "AddCommand.java" in os.listdir(area_shop_dir)
        assert "AreaShopInterface.java" in os.listdir(area_shop_dir)
