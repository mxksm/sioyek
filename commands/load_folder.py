import os
import sys
import subprocess

def load_folder():
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
    
    # close sioyek
    subprocess.run(["pkill", "sioyek"])
    # cd into the directory
    os.chdir(dir_path)
    # open the file in sioyek
    subprocess.run(["sioyek", file_name])

if __name__ == "__main__":
    load_folder()
