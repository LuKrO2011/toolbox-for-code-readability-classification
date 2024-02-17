from src.readability_preprocessing.rdh.temp import RemComController
from src.readability_preprocessing.utils.utils import load_code
from tests.readability_preprocessing.utils.utils import COMMENTS_WITH_DIR

def test_remove_comments():
    rem_com_controller = RemComController()
    code = load_code(COMMENTS_WITH_DIR / "helloWorld.java")
    rem_com_controller.appText = code
    rem_com_controller.split()
    print(rem_com_controller.appText)
