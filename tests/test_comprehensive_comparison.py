"""Comprehensive comparison tests for Syndication API and GraphQL API using test_data.toml"""

import json
import os
import shutil

import ffmpeg
from tomlkit.toml_file import TOMLFile

from src.twitter_video_dl.twitter_video_dl import (
    create_video_urls,
    download_videos,
    extract_media_from_syndication,
    get_img,
    get_tokens,
    get_tweet_details,
    get_tweet_details_syndication,
)

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
    """Remove the destination folder for output files as post-processing"""
    if os.path.exists(OUTPUT_FOLDER_PATH):
        shutil.rmtree(OUTPUT_FOLDER_PATH)


def test_syndication_api_with_all_toml_cases():
    """Test Syndication API (Primary method) with all test_data.toml cases"""
    # Get TOML file
    toml = TOMLFile("./tests/test_data.toml")
    toml_data = toml.read()
    toml_get_data = toml_data.get("tests")

    success_count = 0
    failure_count = 0
    failure_cases = []

    # Test each case
    for test in toml_get_data:
        title = test.get("title")
        url = test.get("url")
        file_name = test.get("file_name")
        expected_files = test.get("expected_files", [])
        acf_list = test.get("audio_check_flag", [])

        print(f"\n{'=' * 80}")
        print(f"[Syndication API] {title}")
        print(f"URL: {url}")
        print(f"Expected files: {expected_files}")

        try:
            # Use Syndication API (Primary method)
            syndication_data = get_tweet_details_syndication(url)
            video_urls, gif_ptn, img_urls = extract_media_from_syndication(
                syndication_data
            )

            # Download images if available
            if image_save_option and img_urls:
                get_img(img_urls, file_name, OUTPUT_FOLDER_PATH)

            # Download videos
            if video_urls:
                download_videos(video_urls, file_name, OUTPUT_FOLDER_PATH, gif_ptn)

            # Verify downloaded files
            for expected_file, acf in zip(expected_files, acf_list):
                file_path = os.path.join(OUTPUT_FOLDER_PATH, expected_file)

                # Check file exists
                assert os.path.exists(file_path), f"File {file_path} does not exist!"

                # Check video/image file integrity
                if expected_file.endswith((".mp4", ".gif")):
                    check_video(file_path, audio_check_flag=acf)

                # Clean up
                os.remove(file_path)

            success_count += 1
            print(f"✅ PASSED: {title}")

        except Exception as e:
            failure_count += 1
            failure_cases.append({"title": title, "url": url, "error": str(e)})
            print(f"❌ FAILED: {title}")
            print(f"   Error: {e}")

    # Summary
    print(f"\n{'=' * 80}")
    print("[Syndication API] Test Summary")
    print(f"Total: {len(toml_get_data)} cases")
    print(f"Success: {success_count} ✅")
    print(f"Failure: {failure_count} ❌")

    if failure_cases:
        print("\nFailed cases:")
        for case in failure_cases:
            print(f"  - {case['title']}: {case['error']}")

    # Assert all cases passed
    assert failure_count == 0, f"{failure_count} test case(s) failed"


def test_graphql_api_with_all_toml_cases():
    """Test GraphQL API (Fallback method) with all test_data.toml cases"""
    # Get TOML file
    toml = TOMLFile("./tests/test_data.toml")
    toml_data = toml.read()
    toml_get_data = toml_data.get("tests")

    success_count = 0
    failure_count = 0
    failure_cases = []

    # Test each case
    for test in toml_get_data:
        title = test.get("title")
        url = test.get("url")
        file_name = test.get("file_name")
        expected_files = test.get("expected_files", [])
        acf_list = test.get("audio_check_flag", [])

        print(f"\n{'=' * 80}")
        print(f"[GraphQL API] {title}")
        print(f"URL: {url}")
        print(f"Expected files: {expected_files}")

        try:
            # Use GraphQL API (Fallback method) with curl-cffi
            bearer_token, guest_token = get_tokens(url)
            resp = get_tweet_details(url, guest_token, bearer_token)
            video_urls, gif_ptn, img_urls = create_video_urls(resp.text)

            # Download images if available
            if image_save_option and img_urls:
                get_img(img_urls, file_name, OUTPUT_FOLDER_PATH)

            # Download videos
            if video_urls:
                download_videos(video_urls, file_name, OUTPUT_FOLDER_PATH, gif_ptn)

            # Verify downloaded files
            for expected_file, acf in zip(expected_files, acf_list):
                file_path = os.path.join(OUTPUT_FOLDER_PATH, expected_file)

                # Check file exists
                assert os.path.exists(file_path), f"File {file_path} does not exist!"

                # Check video/image file integrity
                if expected_file.endswith((".mp4", ".gif")):
                    check_video(file_path, audio_check_flag=acf)

                # Clean up
                os.remove(file_path)

            success_count += 1
            print(f"✅ PASSED: {title}")

        except Exception as e:
            failure_count += 1
            failure_cases.append({"title": title, "url": url, "error": str(e)})
            print(f"❌ FAILED: {title}")
            print(f"   Error: {e}")

    # Summary
    print(f"\n{'=' * 80}")
    print("[GraphQL API] Test Summary")
    print(f"Total: {len(toml_get_data)} cases")
    print(f"Success: {success_count} ✅")
    print(f"Failure: {failure_count} ❌")

    if failure_cases:
        print("\nFailed cases:")
        for case in failure_cases:
            print(f"  - {case['title']}: {case['error']}")

    # Assert all cases passed
    assert failure_count == 0, f"{failure_count} test case(s) failed"


def check_video(video_file_path: str, audio_check_flag: bool = False) -> None:
    """Test function to check for the existence of video and audio streams

    Args:
        video_file_path (str): Path of the video file containing the filename (relative path)
        audio_check_flag (bool, optional): Flag variable to check or set the audio stream (Defaults to False)
    """
    # Load video files in FFmpeg
    try:
        probe = ffmpeg.probe(video_file_path)
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
