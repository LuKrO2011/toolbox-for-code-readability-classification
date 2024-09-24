from readability_preprocessing.sampling.stratified_sampling import calculate_features

input_folder = "/Users/lukas/Documents/Code for Study/Krod Badly Readable"
output_folder = "/Users/lukas/Documents/Code for Study"

if __name__ == "__main__":
    calculate_features(input_dir=input_folder, output_dir=output_folder)
