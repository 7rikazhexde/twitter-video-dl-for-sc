#!.venv/bin/python3

import re
import subprocess
import sys
from typing import Optional, Tuple

from tomlkit.toml_file import TOMLFile


def compare_versions(version1: str, version2: str) -> int:
    """Compare specified versions

    Args:
        version1 (str): [major].[minor].[pathch]
        version2 (str): [major].[minor].[pathch]

    Returns:
        Return comparison result
        int:
            v1 < v2: -1
            v1 > v2: 1
            v1 = v2: 0
    """
    v1 = [int(num) for num in version1.split(".")]
    v2 = [int(num) for num in version2.split(".")]
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def remote_tag_checker(remote: str, tag: Optional[str]) -> bool:
    """Checks if the string (git tag version) specified in the argument can be added to a remote tag

    Args:
        remote (str): remote repository
        tag (Optional[str]): v[major].[minor].[pathch]

    Raises:
        SystemExit: invalid tag version
        subprocess.CalledProcessError: Failed to fetch remote tags

    Returns:
        bool:
            True: git add allowed
            False: gitadd not allowed
    """
    checker = False
    try:
        # Get remote branch tags
        tags = subprocess.run(
            ["git", "ls-remote", "--tags", remote], capture_output=True, text=True
        ).stdout.splitlines()

        if not tags:
            print("No tags found in the remote repository. Create a new tag.")
            return True

        pattern = r"v(\d+\.\d+\.\d+)"
        match = re.search(pattern, tags[-1])
        if match:
            highest_tag = "v" + match.group(1)

        if (
            tag is not None
            and compare_versions(tag.lstrip("v"), highest_tag.lstrip("v")) <= 0
        ):
            error_message = f"Remote tag '{tag}' is an invalid tag version. Exiting the program. Please check pyproject.toml / version."
            sys.exit(error_message)
        checker = True

    except subprocess.CalledProcessError as e:
        error_code = e.returncode
        error_output = e.stderr
        print(f"error_code:{error_code}")
        print(f"error_output:{error_output}")
        error_message = "Failed to fetch remote tags. Exiting the program."
        sys.exit(error_message)
    return checker


def local_tag_checker(tag: Optional[str]) -> bool:
    """Checks if the string (git tag version) specified in the argument can be added to a local tag

    Args:
        tag (Optional[str]): v[major].[minor].[pathch]

    Raises:
        SystemExit: invalid tag version
        subprocess.CalledProcessError: no tags found

    Returns:
        bool:
            True: git add allowed
            False: gitadd not allowed
    """
    checker = False
    try:
        # Get tags sorted in descending order (n,n-1,n-2)
        tags = subprocess.run(
            ["git", "tag", "--sort", "-v:refname"], capture_output=True, text=True
        ).stdout.splitlines()

        if not tags:
            print("No tags found in the local repository. Create a new tag")
            return True

        if (
            tag is not None
            and compare_versions(tag.lstrip("v"), tags[0].lstrip("v")) <= 0
        ):
            error_message = f"Local tag '{tag}' is an invalid tag version. Exiting the program. Please check pyproject.toml / version."
            sys.exit(error_message)
        checker = True
    except subprocess.CalledProcessError as e:
        error_code = e.returncode
        error_output = e.stderr
        print(f"error_code:{error_code}")
        print(f"error_output:{error_output}")
        error_message = "No tags found. Exiting the program."
        sys.exit(error_message)
    return checker


def read_poetry_project_version() -> Tuple[bool, Optional[str]]:
    """Get the "version" value of the "poetry" key from "pyproject.toml"

    Raises:
        SystemExit:
            pyproject.toml does not exist
            version does not exist

    Returns:
        Tuple[bool, Optional[str]]: Acquisition decision result and [major]. [minor]. [pathch].
    """
    read_success_flag = False
    curent_ver = ""
    try:
        # Load the pyproject.toml file
        toml = TOMLFile("pyproject.toml")
        toml_data = toml.read()
        toml_get_data = toml_data.get("tool", {})
        if "poetry" in toml_get_data:
            curent_ver = toml_get_data["poetry"].get("version", "")
            read_success_flag = True
        else:
            error_message = (
                "Failed to find 'poetry' section in pyproject.toml. Exit the program."
            )
            sys.exit(error_message)
    except Exception as e:
        error_message = f"Failed to update pyproject.toml. Error: {str(e)}"
        sys.exit(error_message)
    return read_success_flag, curent_ver


def get_arg(tag: str) -> str:
    """Version specified by command line arguments

    Args:
        tag (str): v[major].[minor].[pathch]

    Raises:
        SystemExit: Invalid tag format

    Returns:
        str: v[major].[minor].[pathch]
    """
    if len(sys.argv) == 2:
        new_tag = sys.argv[1]
        pattern = r"^v[0-9]+\.[0-9]{1,3}\.[0-9]{1,3}$"
        if not re.match(pattern, new_tag):
            # If an argument is incorrectly specified
            error_message = (
                "Invalid tag format. Please enter in [vx.x.x]. Exit the program."
            )
            sys.exit(error_message)
    elif len(sys.argv) > 2:
        error_message = "Invalid tag format. Please enter ./create_tag_data.py [vx.x.x] Exit the program."
        sys.exit(error_message)
    else:
        new_tag = tag
    return new_tag


if __name__ == "__main__":  # pragma: no cover
    remote_to_check = "origin"
    remote_tag_checker_flag = False
    local_tag_checker_flag = False
    read_success_flag, new_tag = read_poetry_project_version()
    new_tag = f"v{new_tag or ''}"
    new_tag = get_arg(new_tag)
    remote_tag_checker_flag = remote_tag_checker(remote_to_check, new_tag)
    local_tag_checker_flag = local_tag_checker(new_tag)
    # Create a new tag
    if remote_tag_checker_flag is True and local_tag_checker_flag is True:
        subprocess.run(["git", "tag", new_tag])
    subprocess.run(["git", "tag"])
