import os
import sys
import requests

URL = "https://barista-f23.fly.dev/f24"
VERSION = "4"
OUT_FOLDER = "fall-24-autograder/v4/"
FILE_NAME = "lazy"


def create_unique_file(folder, file_name, input, output):
    # Ensure the folder exists
    if not os.path.exists(folder):
        print(f"Error: The folder '{folder}' does not exist.")
        return

    # Generate the base file name
    base_name = f"test_{file_name}_"
    extension = ".br"
    count = 1

    # Find the lowest count that avoids file duplication
    while os.path.exists(os.path.join(folder, f"{base_name}{count}{extension}")):
        count += 1

    # Full file path
    full_path = os.path.join(folder, f"{base_name}{count}{extension}")

    # Write the content to the file
    with open(full_path, "w") as file:
        file.write(f"{input}\n\n\n/*\n*OUT*\n{output}\n*OUT*\n*/")

    print(f"File created: {full_path}")


def get_output(input_file, out_subfolder, out_filename):
    # Read the value for program from the file "tmp.br"
    try:
        with open(input_file, "r") as file:
            program = (
                file.read().strip()
            )  # Read and strip any extra whitespace or newlines
    except FileNotFoundError:
        print("Error: File 'tmp.br' not found.")
        return
    except Exception as e:
        print(f"Error reading file 'tmp.br': {e}")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"program": program, "stdin": "", "version": VERSION}

    # Send a POST request
    response = requests.post(URL, json=payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Successfully received response
        res = response.json()
        out = "\n".join(res["res"])
        fail_or_pass = "fails" if "_ERROR" in out else "tests"
        out_file_name = out_subfolder + fail_or_pass
        create_unique_file(out_file_name, out_filename, program, out)
    else:
        print(f"Failed with status code: {response.status_code}")
        print("Response text:", response.text)


if __name__ == "__main__":
    get_output("generate_test.br", OUT_FOLDER, FILE_NAME)
