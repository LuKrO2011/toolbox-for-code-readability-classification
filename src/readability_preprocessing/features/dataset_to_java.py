import os
from datasets import load_dataset

# Load the dataset from Hugging Face
dataset = load_dataset("se2p/code-readability-krod")

# Define the output folder
output_folder = "/Users/lukas/Documents/Code for Study/Krod Well Readable"
os.makedirs(output_folder, exist_ok=True)

# Filter the dataset and save each code snippet with the matching score of 3.68
for record in dataset['train']:
    if record['score'] == 3.68:
        code_snippet = record['code_snippet']
        file_name = record['name']

        # Define the output path with the corresponding name
        output_path = os.path.join(output_folder, f"{file_name}.java")

        # Write the code snippet to the file
        with open(output_path, 'w') as file:
            file.write(code_snippet)

print(f"Code snippets with score 3.68 have been saved to '{output_folder}'")
