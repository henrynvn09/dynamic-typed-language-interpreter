import os
import shutil

# Define folder paths
folder1 = "fails"  # Path to the folder with fewer files
folder2 = "tests"  # Path to the folder with more files
output_folder = "unmatched_files"  # Path to move unmatched files

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get the set of file names from both folders
folder1_files = set(os.listdir(folder1))
folder2_files = set(os.listdir(folder2))

# Find files that are in folder2 but not in folder1
unmatched_files = folder2_files - folder1_files

# Move unmatched files to the output folder
for filename in unmatched_files:
    source_path = os.path.join(folder2, filename)
    destination_path = os.path.join(output_folder, filename)
    shutil.move(source_path, destination_path)
    print(f"Moved {filename} to {output_folder}")

print("Unmatched files have been moved.")

