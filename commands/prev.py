import os
import sys
import subprocess

def get_prev_file():
    # Get the current file path from Sioyek
    current_file = sys.argv[1]  # Sioyek passes the current file path as an argument
#    print(f"Current file: {current_file}")

    if not current_file or current_file == "":
#        print("No file currently open")
        return

    # Extract directory and filename
    dir_path = os.path.dirname(current_file)[1:]
    file_name = os.path.basename(current_file)[:-1]
#    print(f"Directory: {dir_path}")
#    print(f"File name: {file_name}")

    # Get all PDF files in the directory
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(".pdf")])

    # Find the previous file lexicographically
    if file_name in files:
        index = files.index(file_name)
        prev_file = files[index - 1]
#        print(f"@open {os.path.join(dir_path, prev_file)}")  # Command for Sioyek
        subprocess.run(["sioyek", os.path.join(dir_path, prev_file)])
#    else:
#        print("Current file not found in directory list")

if __name__ == "__main__":
    get_prev_file()

