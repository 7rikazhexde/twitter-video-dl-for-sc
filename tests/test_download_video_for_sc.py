import json
import os
import shutil

import ffmpeg
import pytest
from tomlkit.toml_file import TOMLFile

from src.twitter_video_dl.twitter_video_dl import download_video_for_sc

OUTPUT_FOLDER_PATH = "./tests/output"

# Open setting file
with open("./src/twitter_video_dl/settings.json", "r") as f:
    data = json.load(f)

# Get the value of convert_gif_flag
convert_gif_flag = data["gif"]["convert_gif_flag"]

# Get ffmpeg loglevel
ffmpeg_loglevel = data["ffmpeg"]["loglevel"]

# Get image save option
image_save_option = data["image"]["save_option"]


def teardown_function(function):
    # Remove the destination folder for output files as post-processing
    if os.path.exists(OUTPUT_FOLDER_PATH):
        shutil.rmtree(OUTPUT_FOLDER_PATH)


def test_download_video_failure():
    # Test function for cases where URL is not appropriate
    url = "https://x.com/tw_7rikazhexde/status/hogehoge"
    with pytest.raises(AssertionError) as e_info:
        download_video_for_sc(url, "", output_folder_path=OUTPUT_FOLDER_PATH)
    assert (
        str(e_info.value)
        == "Could not parse tweet id from your url.  Make sure you are using the correct url.  If you are, then file a GitHub issue and copy and paste this message.  Tweet url: https://x.com/tw_7rikazhexde/status/hogehoge"
    )


def test_download_videos():
    # Forking source test case-based test function

    # Get TOML file
    toml = TOMLFile("./tests/test_data.toml")
    toml_data = toml.read()
    toml_get_data = toml_data.get("tests")  # Change "videos" to "tests"

    # Get the "url" and "file_name" of each element to see if the video can be retrieved and saved correctly
    for test in toml_get_data:  # Change "video" to "test"
        url = test.get("url")
        file_name = test.get("file_name")  # Get the file_name from TOML
        download_video_for_sc(
            url, file_name, output_folder_path=OUTPUT_FOLDER_PATH
        )  # Pass file_name to download_video_for_sc
        expected_files = test.get(
            "expected_files", []
        )  # Get expected_files list from TOML
        acf_list = test.get("audio_check_flag", [])
        for expected_file, acf in zip(
            expected_files, acf_list
        ):  # Iterate through expected_files list and corresponding audio_check_flag list
            print(f"acf={acf} / expected_file={expected_file}")
            file_path = os.path.join(OUTPUT_FOLDER_PATH, expected_file)
            check_file(file_path)
            check_video(
                file_path, audio_check_flag=acf
            )  # Call check_video for each expected_file
            os.remove(file_path)


def check_file(file_path: str) -> None:
    """Check if the file exists.

    Args:
        file_path (str): Path of the file to check.

    Raises:
        AssertionError: If the file does not exist.
    """
    assert os.path.exists(file_path), f"File {file_path} does not exist!"


def check_video(video_file_path: str, audio_check_flag: bool = False) -> None:
    """Test function to check for the existence of video and audio streams for a video file specified by path

    Args:
        video_file_path (str): Path of the video file containing the filename (relative path)
        audio_check_flag (bool, optional): Flag variable to check or set the audio stream(Defaults to False)
    """
    # Load video files in FFmpeg
    try:
        probe = ffmpeg.probe(video_file_path)
        # Run with the -s option to display standard output
        print(probe)
    except ffmpeg.Error as e:
        assert False, f"Failed to probe video file: {e.stderr}"

    # Verify video is loaded correctly and stream exists
    assert "streams" in probe, "No streams found in the video"

    # Get first video stream
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )

    # Verify video stream exists
    assert video_stream is not None, "No video stream found in the video"

    if audio_check_flag:
        # Get the first audio stream
        audio_stream = next(
            (stream for stream in probe["streams"] if stream["codec_type"] == "audio"),
            None,
        )

        # Verify that audio stream exists
        assert audio_stream is not None, "No audio stream found in the video"
