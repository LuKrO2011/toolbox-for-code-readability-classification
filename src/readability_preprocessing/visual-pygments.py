import imgkit
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import JavaLexer
from PIL import Image
import re

DEFAULT_OUT = 'out.png'
DEFAULT_CSS = 'towards.css'
HEX_REGEX = r'#[0-9a-fA-F]{6}'


def _load_colors_from_css(file: str,
                          hex_colors_regex: str = HEX_REGEX) -> set[str]:
    """
    Load the css file and return the colors in it using the regex
    :param file: path to the css file
    :param hex_colors_regex: regex to find the colors
    :return: list of colors
    """
    with open(file, 'r') as f:
        css_code = f.read()

    colors = re.findall(hex_colors_regex, css_code, re.MULTILINE)

    return set(colors)


def _convert_hex_to_rgba(hex_colors: set[str]) -> set[tuple[int, int, int, int]]:
    """
    Convert the hex colors to rgba
    :param hex_colors: set of hex colors
    :return: set of rgba colors
    """
    return {
        tuple(int(allowed_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
        for
        allowed_color in hex_colors}


def _remove_blur(img: Image, width: int, height: int,
                 allowed_colors: set[tuple[int, int, int, int]]) -> Image:
    """
    Remove the blur from the image.
    Set all the pixels that are not in the allowed colors to the closest allowed color.
    :param img: The image
    :param width: The width of the image
    :param height: The height of the image
    :param allowed_colors: The allowed colors
    :return: The image without blur
    """
    for i in range(width):
        for j in range(height):
            if img.getpixel((i, j)) not in allowed_colors:
                closest_color = min(allowed_colors, key=lambda x: sum(
                    abs(i - j) for i, j in zip(x, img.getpixel((i, j)))))
                img.putpixel((i, j), closest_color)

    return img


def code_to_image(code: str, output: str = DEFAULT_OUT, css: str = DEFAULT_CSS,
                  width: int = 128,
                  height: int = 128):
    """
    Convert the given Java code to a visualisation/image.
    :param code: The code
    :param output: The path to save the image
    :param css: The css to use for styling the code
    :param width: The width of the image
    :param height: The height of the image
    :return: The image
    """
    # Convert the code to html
    lexer = JavaLexer()
    formatter = HtmlFormatter()
    html = highlight(code, lexer, formatter)

    # Set the options for imgkit
    options = {
        "format": "png",
        "quality": "100",
        "crop-h": str(height),
        "crop-w": str(width),
        "crop-x": '0',
        "crop-y": '0',
        "encoding": "UTF-8",
        "quiet": '',
        "disable-smart-width": '',
        "width": str(width),
        "height": str(height)
    }

    # Convert the html code to image
    imgkit.from_string(html, output, css=css, options=options)

    # Open the image
    img = Image.open(output)

    # Remove the blur from the image
    allowed_colors = _load_colors_from_css(css)
    allowed_colors = _convert_hex_to_rgba(allowed_colors)
    img = _remove_blur(img, width, height, allowed_colors)

    # Save the image
    img.save(output)


# Sample Java code
code = """
// A method for counting
public void getNumber(){
    int count = 0;
    while(count < 10){
        count++;
    }
}
"""
output_name = "code.png"


def main() -> None:
    code_to_image(code, output_name)

    # Show the image
    img = Image.open(output_name)
    img.show()


if __name__ == "__main__":
    main()

code_to_image(code)
