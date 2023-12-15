import os
import shutil

import ffmpeg
import pytest

from src.twitter_video_dl.twitter_video_dl import download_video_for_sc

OUTPUT_FOLDER_PATH = "./tests/output"


def test_download_video4_success():
    """Test function for the case where multiple video files are submitted in one post"""
    url = "https://x.com/tw_7rikazhexde/status/1710678217575801015?s=20"
    download_video_for_sc(url, "test", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/test_1.mp4", audio_check_flag=True)
    check_video(f"{OUTPUT_FOLDER_PATH}/test_2.mp4", audio_check_flag=True)
    check_video(f"{OUTPUT_FOLDER_PATH}/test_3.mp4", audio_check_flag=True)
    check_video(f"{OUTPUT_FOLDER_PATH}/test_4.mp4", audio_check_flag=True)


def test_download_video1_success():
    """Test function for the case where one video file is submitted in one post (with output file name specified)"""
    url = "https://x.com/tw_7rikazhexde/status/1710868951109124552?s=20"
    download_video_for_sc(url, "test", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/test.mp4", audio_check_flag=True)


def test_download_video_non_filename_success():
    """Test function for the case where one video file is submitted in one post (no output file name specified)"""
    url = "https://x.com/tw_7rikazhexde/status/1710868951109124552?s=20"
    download_video_for_sc(url, "", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/1710868926161399808.mp4", audio_check_flag=True)


def test_download_video_failure():
    """Test function for cases where URL is not appropriate"""
    url = "https://x.com/tw_7rikazhexde/status/hogehoge"
    with pytest.raises(AssertionError) as e_info:
        download_video_for_sc(url, "", output_folder_path=OUTPUT_FOLDER_PATH)
    assert (
        str(e_info.value)
        == "Could not parse tweet id from your url.  Make sure you are using the correct url.  If you are, then file a GitHub issue and copy and paste this message.  Tweet url: https://x.com/tw_7rikazhexde/status/hogehoge"
    )


def test_download_gif_filename():
    """Test function for cases where a gif file is submitted (with output file name specified)"""
    url = "https://x.com/tw_7rikazhexde/status/1735502484700057703?s=20"
    download_video_for_sc(url, "", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/1735502484700057703.gif")


def test_download_gif_non_filename():
    """Test function for cases where a gif file is submitted (without specifying the output filename)"""
    url = "https://x.com/tw_7rikazhexde/status/1735503057079951364?s=20"
    download_video_for_sc(url, "gif_test", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/gif_test.gif")


def test_download_video1_non_avc1_success():
    """Test function for cases where videos not supporting AVC1 encoding are submitted"""
    url = "https://x.com/tw_7rikazhexde/status/1650804112987136000?s=20"
    download_video_for_sc(url, "test", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/test.mp4", audio_check_flag=True)


def test_download_video1_avc1_success():
    """Test function for the case where a video is submitted that supports AVC1 encoding"""
    url = "https://x.com/tw_7rikazhexde/status/1710868951109124552?s=20"
    download_video_for_sc(url, "test", output_folder_path=OUTPUT_FOLDER_PATH)
    check_video(f"{OUTPUT_FOLDER_PATH}/test.mp4", audio_check_flag=True)


def teardown_function(function):
    """Remove the destination folder for output files as post-processing"""
    if os.path.exists(OUTPUT_FOLDER_PATH):
        shutil.rmtree(OUTPUT_FOLDER_PATH)


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
