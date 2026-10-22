"""Test for the fallback method used when the Syndication API fails.

X's server-rendered tweet page embeds the TweetResultByRestId GraphQL
result directly (as a Relay record), so the fallback parses that out of
the page instead of scraping a bearer token out of a main.js bundle - the
old main.js-based flow no longer works against X's current frontend.
"""

import json
import os
import shutil

import pytest

from src.twitter_video_dl.twitter_video_dl import (
    TwitterVideoDLError,
    extract_media_from_tweet_result,
    get_tweet_result_from_page,
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
    # Remove the destination folder for output files as post-processing
    if os.path.exists(OUTPUT_FOLDER_PATH):
        shutil.rmtree(OUTPUT_FOLDER_PATH)


def test_fallback_get_tweet_result_from_page():
    """Test that the embedded TweetResultByRestId result can be fetched and parsed"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    result = get_tweet_result_from_page(test_url)

    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("__typename") == "Tweet", "Result should be a Tweet"
    assert "media_entities2" in result, "Result should contain media_entities2"


def test_fallback_extract_video_urls():
    """Test that video URLs can be extracted from the embedded tweet result"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    result = get_tweet_result_from_page(test_url)
    video_urls, gif_ptn, img_urls = extract_media_from_tweet_result(result)

    assert len(video_urls) > 0, "Should extract at least one video URL"
    assert all(url.startswith("http") for url in video_urls), (
        "All video URLs should be valid"
    )
    assert isinstance(gif_ptn, bool), "gif_ptn should be boolean"
    assert isinstance(img_urls, list), "img_urls should be a list"


def test_fallback_with_image_tweet():
    """Test that both videos and images are extracted from a mixed-media tweet"""
    test_url = "https://x.com/tw_7rikazhexde/status/1754040936005538201"

    result = get_tweet_result_from_page(test_url)
    video_urls, gif_ptn, img_urls = extract_media_from_tweet_result(result)

    assert len(video_urls) > 0, "Should extract videos"
    if image_save_option:
        assert len(img_urls) > 0, (
            "Should extract images when image_save_option is enabled"
        )


def test_fallback_with_gif_tweet():
    """Test that an animated GIF tweet is reported as a GIF"""
    test_url = "https://x.com/tw_7rikazhexde/status/1735502484700057703"

    result = get_tweet_result_from_page(test_url)
    video_urls, gif_ptn, img_urls = extract_media_from_tweet_result(result)

    assert len(video_urls) > 0, "Should extract the animated GIF as a video URL"
    assert gif_ptn is True, "gif_ptn should be True for an animated_gif tweet"


def test_fallback_invalid_tweet_id():
    """Test that an invalid tweet URL raises TwitterVideoDLError"""
    invalid_url = "https://x.com/tw_7rikazhexde/status/invalid"

    with pytest.raises(TwitterVideoDLError):
        get_tweet_result_from_page(invalid_url)
