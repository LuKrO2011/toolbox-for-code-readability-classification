import imgkit
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import JavaLexer
from PIL import Image

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

# Lex the code
lexer = JavaLexer()
tokens = lexer.get_tokens(code)

# Print the lexed tokens
for token in tokens:
    print(token)

# Convert the code to html
formatter = HtmlFormatter()
print(formatter.get_style_defs())
html_code = highlight(code, lexer, formatter)

# Print the html code
print(html_code)

# Set the width and height of the image
width = 128
height = 128

# Set the options
options = {
    # 'extended-help': '',
    "format": "png",
    "quality": "100",
    "crop-h": str(height),
    "crop-w": str(width),
    "crop-x": '0',
    "crop-y": '0',
    "encoding": "UTF-8",
    # "quiet": '',
    "disable-smart-width": '',
    "width": str(width),
    "height": str(height)
}
css = 'towards.css'

# Convert the html code to image
imgkit.from_string(html_code, 'out.png', css=css, options=options)

# Load the image
img = Image.open('out.png')

# Define allowed colors
allowed_colors = ['#006200', '#fa0200', '#fefa01', '#01ffff', '#ffffff']

# Convert the colors to rgba
allowed_colors = [
    tuple(int(allowed_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for
    allowed_color in allowed_colors]

# Set all the pixels that are not in the allowed colors to the closest allowed color
for i in range(width):
    for j in range(height):
        if img.getpixel((i, j)) not in allowed_colors:
            closest_color = min(allowed_colors, key=lambda x: sum(
                abs(i - j) for i, j in zip(x, img.getpixel((i, j)))))
            img.putpixel((i, j), closest_color)

# Save the image
img.save('out.png')

# Attach the css at the beginning of the html code
html_code = '<style>' + open(css, 'r').read() + '</style>' + html_code

# Open the html code in the browser (with css)
with open('out.html', 'w') as f:
    f.write(html_code)
