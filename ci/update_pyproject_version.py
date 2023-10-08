#!.venv/bin/python3

import re
import subprocess
import sys
from typing import Optional, Tuple

from tomlkit.toml_file import TOMLFile


def update_poetry_project_version(new_tag: str, toml: TOMLFile) -> None:
    """Update [poetry].[version] in pyproject.toml

    Args:
        new_tag (str): v[major].[minor].[pathch]
        toml (TOMLFile): TOMLFile("pyproject.toml")

    Raises:
        KeyError: Failed to update pyproject.toml
    """
    toml_data = toml.read()
    try:
        # Update version
        toml_get_data = toml_data.get("tool")
        if toml_get_data is not None and "poetry" in toml_get_data:
            toml_get_data["poetry"]["version"] = new_tag
            # Writing the pyproject.toml file
            toml.write(toml_data)
        else:
            raise KeyError("Failed to find 'poetry' section in 'tool'")

    except Exception as e:
        error_message = f"Failed to update pyproject.toml. Error: {str(e)}"
        sys.exit(error_message)


def get_arg() -> Optional[str]:
    """Version specified by command line arguments

    Args:
        tag (str): [major].[minor].[pathch]

    Raises:
        SystemExit: Invalid tag format([major].[minor].[pathch])

    Returns:
        str: [major].[minor].[pathch]
    """
    if len(sys.argv) == 2:
        new_tag = sys.argv[1]
        pattern = r"^[0-9]+\.[0-9]{1,3}\.[0-9]{1,3}$"
        if not re.match(pattern, new_tag):
            # If an argument is incorrectly specified
            error_message = (
                "Invalid tag format. Please enter in [x.x.x]. Exit the program."
            )
            sys.exit(error_message)
    elif len(sys.argv) > 2:
        error_message = "Please enter ./create_tag_data.py [x.x.x] Exit the program."
        sys.exit(error_message)
    else:
        new_tag = None
    return new_tag


def create_ver(input_ver: Optional[str]) -> Tuple[bool, str, TOMLFile]:
    """Create infomations of [poetry].[version] in pyproject.toml

    Args:
        input_ver (Optional[str]): [major].[minor].[pathch]

    Returns:
        Tuple[bool, str, TOMLFile]: Infomation of [poetry].[version] in pyproject.toml
    """
    # Load the pyproject.toml file
    toml = TOMLFile("pyproject.toml")
    toml_data = toml.read()
    toml_get_data = toml_data.get("tool")
    # Update version
    if toml_get_data is not None and "poetry" in toml_get_data:
        current_data = toml_get_data["poetry"].get("version")
    else:
        current_data = "0.0.0"
    major, minor, patch = map(int, current_data.split("."))
    create_tag_flag = False
    # Argument specified data available
    if input_ver is not None:
        new_ver = input_ver
        create_tag_flag = True
        # Error if less than version of pyproject.toml
        if input_ver <= current_data:
            create_tag_flag = False
            error_message = f"The specified tag '{input_ver}' must be greater than the latest tag 'v{current_data}'. Exit the program."
            sys.exit(error_message)
    # No data specified in argument
    else:
        # Increment version in pyproject.toml
        if patch < 999:
            patch += 1
        elif minor < 999:
            minor += 1
            patch = 0
        else:
            major += 1
            minor = 0
            patch = 0
        new_ver = f"{major}.{minor}.{patch}"
        create_tag_flag = True
    return create_tag_flag, new_ver, toml


def git_add_if_diff(directory: str) -> None:
    """Run the git diff command to see if there are any differences

    Args:
        directory (str): directory name
    """
    result = subprocess.run(
        ["git", "diff", "--quiet", "--exit-code", directory], capture_output=True
    )

    if result.returncode != 0:
        # If there is a difference, run the git add command
        subprocess.run(["git", "add", directory])
        print(f"{__file__}: git add {directory}")
    else:
        print(f"{__file__}: There is no difference in {directory}")


if __name__ == "__main__":  # pragma: no cover
    # Check for correct data format
    input_ver = get_arg()
    # Without argument: Increment version of pyproject.toml
    # With argument: update if version is greater than version of pyproject.toml
    create_tag_flag, new_ver, toml = create_ver(input_ver)
    if create_tag_flag:
        update_poetry_project_version(new_ver, toml)
        subprocess.run(["git", "add", "pyproject.toml"])
