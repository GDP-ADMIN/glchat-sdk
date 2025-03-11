"""This script updates the pyproject.toml file to change the dependency from source code to the binary version.

Author:
    - Muhammad Hakim Asy'ari <muhammad.h.asyari@gdplabs.id>
    - Restu Agung Parama <Restu.a.parama@gdplabs.id>

References:
    - https://github.com/GDP-ADMIN/gen-ai-internal/blob/main/libs/update_pyproject.py
"""

import base64
import hashlib
import os
import sys
import zipfile


def generate_sha256(file_path):
    """Generate SHA-256 hash and convert to base64 URL-safe encoding."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256_hash.update(chunk)

    sha256 = sha256_hash.hexdigest()
    base64_hash = (
        base64.urlsafe_b64encode(bytes.fromhex(sha256)).decode("utf-8").rstrip("=")
    )

    return base64_hash


def generate_record(file_path):
    """Generate a record in the format: file_path,sha256=<base64_hash>,<file_size>."""
    base64_hash = generate_sha256(file_path)
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    return f"{file_name},sha256={base64_hash},{file_size}"


def add_file_to_whl(whl_file, file_path, arcname):
    """Add a file to the .whl file."""
    with zipfile.ZipFile(whl_file, "a", zipfile.ZIP_DEFLATED) as whl:
        if arcname not in whl.namelist():
            whl.write(file_path, arcname)
            print(f"Added {file_path} as {arcname} to {whl_file}")
        else:
            print(f"File {arcname} already exists in {whl_file}, skipping.")


def update_record_in_whl(whl_file, record_lines, folder_name_to_remove):
    """Update and replace the RECORD file inside the .whl with the new records.

    Removing lines that start with folder_name_to_remove/.
    """
    # Open the original .whl file in read mode
    with zipfile.ZipFile(whl_file, "r") as whl:
        # Read all files in the .whl archive
        files_in_whl = {file: whl.read(file) for file in whl.namelist()}

        # Find the RECORD file inside the .whl
        record_file = None
        for file in files_in_whl:
            if file.endswith("RECORD"):
                record_file = file
                break

        # Read the existing RECORD file content
        if record_file:
            record_data = files_in_whl[record_file].decode("utf-8")
        else:
            record_data = ""

        # Remove lines that start with folder_name_to_remove/
        record_data = "\n".join([line for line in record_data.splitlines()])

        # Append the new record lines
        updated_record_data = record_data + "\n" + "\n".join(record_lines)

    # Now open the .whl file in write mode to replace the RECORD file
    with zipfile.ZipFile(whl_file, "w", zipfile.ZIP_DEFLATED) as new_whl:
        for file, data in files_in_whl.items():
            # Write files from the original .whl, except the old RECORD file
            if file != record_file:
                new_whl.writestr(
                    file, data
                )  # Write the file content to the new archive

        # Write the updated RECORD file
        new_whl.writestr(record_file, updated_record_data)

    print(f"Replaced RECORD file in {whl_file}")


def update_all_whls_in_dist(folder_path, folder_name_to_remove):
    """Update all .whl files in the specified directory by removing the specified folder."""
    # Determine the file extension based on the operating system
    if os.getenv("RUNNER_OS", "").lower() == "windows":
        extension = ".pyd"
    else:
        extension = ".so"

    parent_directory = os.path.abspath(os.path.join(folder_path, ".."))

    # Loop through all .whl files in the given folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".whl"):
            whl_file = os.path.join(folder_path, file_name)

            record_lines = []
            # After processing, generate the RECORD-like information
            # This assumes we want to include the other files in the final output
            for file in os.listdir(parent_directory):
                if file.endswith(extension) or file.endswith(".pyi"):
                    file_path = os.path.join(parent_directory, file)
                    arcname = os.path.relpath(file_path, parent_directory)

                    add_file_to_whl(whl_file, file_path, arcname)

                    record_lines.append(generate_record(file_path))

            # Write the RECORD information to a file
            update_record_in_whl(whl_file, record_lines, folder_name_to_remove)


if __name__ == "__main__":
    # Example usage: Removing a folder named 'unwanted_folder' from the generated .whl file
    update_all_whls_in_dist("dist", sys.argv[1])
