#!/bin/bash

# Directory containing the files
directory="fails"

# Loop through files in the directory
for file in "$directory"/*; do
  # Check if file is not empty and doesn't contain the string "OUT"
  if [[ -f "$file" && ! $(grep -q "OUT" "$file") ]]; then
    # Remove the file
    rm "$file"
    echo "Removed: $file"
  fi
done

