import numpy as np
from PIL import Image

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import JavaLexer

# Sample Java code
code = """
// This is a comment
int num = 42;
String text = "Hello, World!";
"""

# Highlight the Java code using JavaLexer
highlighted_code = highlight(code, JavaLexer(), TerminalFormatter())

# Create a dictionary to map color categories to RGB values
color_mapping = {
    'Comment': (0, 128, 0),  # Green
    'Keyword': (0, 0, 255),  # Blue
    'Operator': (255, 0, 0),  # Red
    'Identifier': (128, 128, 128),  # Gray
    'Literal': (255, 255, 0),  # Yellow
}


# Function to get the RGB value for a given color category
def get_rgb_value(category):
    return color_mapping.get(category, (255, 255, 255))  # Default to white


# Create a blank image
image_size = (128, 128)
image = Image.new('RGB', image_size)

# Example: Map the color category 'Comment' to the color block
color_category = 'Comment'
rgb_color = get_rgb_value(color_category)
image.putdata([rgb_color] * (image_size[0] * image_size[1]))

# Save the image
image.save('color_block.png')

# Convert to an RGB matrix
rgb_matrix = list(image.getdata())
rgb_matrix = [list(row) for row in rgb_matrix]

# Ensure the matrix shape is (128, 128, 3)
rgb_matrix = np.array(rgb_matrix, dtype=np.uint8).reshape(image_size[1], image_size[0],
                                                          3)

# Save the matrix as png
image = Image.fromarray(rgb_matrix)
image.save('color_block.png')
