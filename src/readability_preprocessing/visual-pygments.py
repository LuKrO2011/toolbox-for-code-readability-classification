import imgkit
from imgkit.config import Config
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import JavaLexer

# Sample Java code
code = """
// A very long comment. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been
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

# Attach the css at the beginning of the html code
html_code = '<style>' + open(css, 'r').read() + '</style>' + html_code

# Open the html code in the browser (with css)
with open('out.html', 'w') as f:
    f.write(html_code)



