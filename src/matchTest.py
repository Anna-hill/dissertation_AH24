import re
from pathlib import Path
from glob import glob


def match_files(folder1_files, folder2_files):
    # Dictionary to store matched files
    matches = {}

    # Compile a regex pattern to extract the number sequence
    pattern = re.compile(r"(\d+\.\d+_\d+\.\d+)")

    # Create a dictionary for folder1 files with the extracted number sequence as keys
    folder1_dict = {}
    for file in folder1_files:
        match = pattern.search(file)
        if match:
            key = match.group(1)
            folder1_dict[key] = file

    # Create a dictionary for folder2 files with the extracted number sequence as keys
    folder2_dict = {}
    for file in folder2_files:
        match = pattern.search(file)
        if match:
            key = match.group(1)
            if key not in folder2_dict:
                folder2_dict[key] = []
            folder2_dict[key].append(file)

    # Iterate over folder1 dictionary and find matches in folder2 dictionary
    for key, file1 in folder1_dict.items():
        if key in folder2_dict:
            matches[file1] = folder2_dict[key]

    return matches


# Example usage:

if __name__ == "__main__":

    als_path = "data/Bonaly/als_dtm"
    sim_path = "data/Bonaly/sim_dtm"
    folder1_files = glob(als_path + "/*.tif")

    folder2_files = glob(sim_path + "/*.tif")

    matched_files = match_files(folder1_files, folder2_files)
    for file1, files2 in matched_files.items():
        # print(f"Matched: {file1} with {files2}")
        for file in files2:
            print("second file: ", file, "first file: ", file1)
