import json
import os
import shutil

import ffmpeg

from src.twitter_video_dl.twitter_video_dl import download_video_for_sc

OUTPUT_FOLDER_PATH = "./tests/output"


def test_download_videos():
    """Forking source test case-based test function"""
    json_file_path = "./tests/TestVideosForShortcuts.json"

    # Load JSON file
    with open(json_file_path, "r") as file:
        data = json.load(file)

    # Get the value of the "videos" key
    videos = data.get("videos", [])

    # Get the "url" and "audio_check_flag" of each element to see if the video can be retrieved and saved correctly
    for video in videos:
        url = video.get("url", "")
        acf = video.get("audio_check_flag", False)
        download_video_for_sc(url, "test", output_folder_path=OUTPUT_FOLDER_PATH)
        if acf:
            print(f"audio_check_flag: {acf}, url: {url}")
            check_video(f"{OUTPUT_FOLDER_PATH}/test.mp4", audio_check_flag=acf)
            os.remove(f"{OUTPUT_FOLDER_PATH}/test.mp4")
        else:
            print(f"audio_check_flag: {acf}, url: {url}")
            check_video(f"{OUTPUT_FOLDER_PATH}/test.gif", audio_check_flag=acf)
            os.remove(f"{OUTPUT_FOLDER_PATH}/test.gif")


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
