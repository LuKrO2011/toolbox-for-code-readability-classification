from src.readability_preprocessing.rdh.temp import RemoveCommentsController
from src.readability_preprocessing.utils.utils import load_code
from tests.readability_preprocessing.utils.utils import COMMENTS_WITH_DIR


def test_remove_comments():
    rem_com_controller = RemoveCommentsController()
    code = load_code(COMMENTS_WITH_DIR / "helloWorld.java")
    new_code = rem_com_controller.remove_comments(code)
    print()
    print(new_code)
