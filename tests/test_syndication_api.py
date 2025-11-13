"""Test for Syndication API (Primary method)"""

import json
import os
import shutil

import pytest

from src.twitter_video_dl.twitter_video_dl import (
    extract_media_from_syndication,
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
    # Remove the destination folder for output files as post-processing
    if os.path.exists(OUTPUT_FOLDER_PATH):
        shutil.rmtree(OUTPUT_FOLDER_PATH)


def test_syndication_api_get_tweet_details():
    """Test Syndication API can fetch tweet details"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Test Syndication API
    syndication_data = get_tweet_details_syndication(test_url)

    # Verify response is valid JSON
    assert isinstance(syndication_data, dict), "Response should be a dictionary"
    assert len(syndication_data) > 0, "Response should not be empty"


def test_syndication_api_extract_media():
    """Test Syndication API can extract video and image URLs"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Get tweet details
    syndication_data = get_tweet_details_syndication(test_url)

    # Extract media
    video_urls, gif_ptn, img_urls = extract_media_from_syndication(syndication_data)

    # Verify video URLs extracted
    assert len(video_urls) > 0, "Should extract at least one video URL"
    assert all(
        url.startswith("http") for url in video_urls
    ), "All video URLs should be valid"

    # Verify gif pattern
    assert isinstance(gif_ptn, bool), "gif_ptn should be boolean"

    # Verify image URLs
    assert isinstance(img_urls, list), "img_urls should be a list"


def test_syndication_api_card_type_video():
    """Test Syndication API can handle card-type videos (promoted tweets)"""
    # Card-type video URL
    test_url = "https://x.com/GOTGTheGame/status/1451361961782906889"

    syndication_data = get_tweet_details_syndication(test_url)
    video_urls, gif_ptn, img_urls = extract_media_from_syndication(syndication_data)

    # Verify video extracted from card
    assert len(video_urls) > 0, "Should extract video from card-type tweet"


def test_syndication_api_image_tweet():
    """Test Syndication API can extract images from tweet"""
    # Tweet with images and videos
    test_url = "https://x.com/tw_7rikazhexde/status/1754040936005538201"

    syndication_data = get_tweet_details_syndication(test_url)
    video_urls, gif_ptn, img_urls = extract_media_from_syndication(syndication_data)

    # Verify both videos and images extracted
    if image_save_option:
        assert (
            len(img_urls) > 0
        ), "Should extract images when image_save_option is enabled"
    assert len(video_urls) > 0, "Should extract videos"


def test_syndication_api_invalid_tweet_id():
    """Test Syndication API handles invalid tweet ID"""
    invalid_url = "https://x.com/tw_7rikazhexde/status/invalid"

    with pytest.raises(AssertionError) as e_info:
        get_tweet_details_syndication(invalid_url)

    assert "Could not parse tweet id" in str(e_info.value)
