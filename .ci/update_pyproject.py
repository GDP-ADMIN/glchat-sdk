"""This script updates the pyproject.toml file to change the dependency from source code to the binary version.

Author:
    - Muhammad Hakim Asy'ari <muhammad.h.asyari@gdplabs.id>
    - Restu Agung Parama <Restu.a.parama@gdplabs.id>

References:
    - https://github.com/GDP-ADMIN/gen-ai-internal/blob/main/libs/update_pyproject.py
"""

import subprocess
import os
import toml
import re


def module_exists(module_name):
    result = subprocess.run(
        ["poetry", "show", module_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


def update_pyproject():
    """Update pyproject.toml file to change the dependency from source code to the binary version."""
    module_list = [
        folder
        for folder in os.listdir("../")
        if os.path.isdir(os.path.join("../", folder)) and "-" in folder
    ]
    print(module_list)

    with open("pyproject.toml", "r", encoding="utf-8") as file:
        pyproject = toml.load(file)

    package_name = pyproject["tool"]["poetry"]["name"].replace("-", "_")
    print(f"Extracted package name: {package_name}")
    tag_name = os.getenv("TAG_NAME", "notag")
    print(f"tag name is {tag_name}")
    if tag_name == "notag":
        current_branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        print(f"the branch is {current_branch}")
        if current_branch not in ["main", "master"]:
            print("Adjust precommit config")
            with open(".pre-commit-config.yaml", "r", encoding="utf-8") as file:
                pre_commit_config = file.read()
            pre_commit_config = pre_commit_config.replace(
                'args: ["-rn", "-sn"]',
                'args: ["-rn", "-sn", "--disable=no-name-in-module"]',
            )
            with open(".pre-commit-config.yaml", "w", encoding="utf-8") as file:
                file.write(pre_commit_config)

    modules_to_add_setup = []

    print("Checking for modules to add to pyproject.toml")

    for module in pyproject["tool"]["poetry"]["dependencies"]:
        if not re.match(r".*?(gllm|bosa).*?", module):
            continue

        tag = pyproject["tool"]["poetry"]["dependencies"][module].get("tag", "")
        start_index = tag.rfind("v") + 1
        version = tag[start_index:]
        extras = pyproject["tool"]["poetry"]["dependencies"][module].get("extras", [])
        if extras:
            extras_str = f"[{','.join(extras)}]"
        else:
            extras_str = ""

        if version:
            modules_to_add_setup.append(f"{module}=={version}{extras_str}")
        else:
            modules_to_add_setup.append(f"{module}{extras_str}")

    if modules_to_add_setup:
        # replace package from git to artifact registry
        # remove existing modules
        for module in modules_to_add_setup:
            clean_module_name = module.split("[")[0].split("==")[0]
            if module_exists(clean_module_name):
                with open("pyproject.toml", "r") as f:
                    pyproject_data = toml.load(f)

                dependencies = (
                    pyproject_data.get("tool", {})
                    .get("poetry", {})
                    .get("dependencies", {})
                )
                if clean_module_name in dependencies:
                    del dependencies[clean_module_name]
                    print(f"Removed {clean_module_name} from dependencies.")

                with open("pyproject.toml", "w") as f:
                    toml.dump(pyproject_data, f)
                print("Updated pyproject.toml successfully.")
            else:
                print(f"Module {clean_module_name} not found. Skipping removal.")

        # add modules from artifact registry
        try:
            subprocess.run(
                ["poetry", "add"] + modules_to_add_setup,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            print("Command failed with error code:", e.returncode)
            print("Output:", e.stdout.decode())
            print("Error:", e.stderr.decode())

    # Add setup.py step
    print("Adding setup.py file")
    with open("setup.py", "w", encoding="utf-8") as setup_file:
        setup_file.write(
            """#!/usr/bin/env python

import setuptools

if __name__ == "__main__":
    setuptools.setup()
"""
        )
    print("setup.py file has been created successfully.")


def modify_pyproject(file_path):
    try:
        # Load the pyproject.toml file
        with open(file_path, "r") as file:
            pyproject_data = toml.load(file)

        # Update the build-system.requires
        if "build-system" in pyproject_data:
            requires = pyproject_data["build-system"].get("requires", [])
            if "setuptools" not in requires:
                requires.append("setuptools")
                pyproject_data["build-system"]["requires"] = requires
        else:
            raise KeyError("No [build-system] section found in pyproject.toml")

        # Add the [tool.poetry.build] section
        if "tool" not in pyproject_data:
            pyproject_data["tool"] = {}
        if "poetry" not in pyproject_data["tool"]:
            pyproject_data["tool"]["poetry"] = {}
        pyproject_data["tool"]["poetry"]["build"] = {
            "script": "build.py",
            "generate-setup-file": True,
        }

        # Write the updated data back to pyproject.toml
        with open(file_path, "w") as file:
            toml.dump(pyproject_data, file)

        print(f"Successfully updated {file_path}")

    except Exception as e:
        print(f"Error updating pyproject.toml: {e}")


if __name__ == "__main__":
    update_pyproject()
    modify_pyproject("pyproject.toml")
