"""Test for GraphQL API with curl-cffi (Fallback method)"""

import json
import os
import shutil

import pytest

from src.twitter_video_dl.twitter_video_dl import (
    create_video_urls,
    get_tokens,
    get_tweet_details,
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


def test_graphql_api_get_tokens():
    """Test GraphQL API can get bearer token, guest token, and query ID"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Get tokens with curl-cffi
    bearer_token, guest_token, query_id = get_tokens(test_url)

    # Verify bearer token
    assert bearer_token is not None, "Bearer token should not be None"
    assert len(bearer_token) > 0, "Bearer token should not be empty"
    assert bearer_token.startswith("AAAAAAA"), "Bearer token should start with AAAAAAA"

    # Verify guest token
    assert guest_token is not None, "Guest token should not be None"
    assert len(guest_token) > 0, "Guest token should not be empty"
    assert guest_token.isdigit(), "Guest token should be numeric"

    # Verify query ID
    assert query_id is not None, "Query ID should not be None"
    assert len(query_id) > 0, "Query ID should not be empty"


def test_graphql_api_get_tweet_details():
    """Test GraphQL API can fetch tweet details with curl-cffi"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Get tokens
    bearer_token, guest_token, query_id = get_tokens(test_url)

    # Get tweet details via GraphQL API
    resp = get_tweet_details(test_url, guest_token, bearer_token, query_id)

    # Verify response
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
    assert len(resp.text) > 0, "Response text should not be empty"

    # Verify response is valid JSON
    json_data = json.loads(resp.text)
    assert isinstance(json_data, dict), "Response should be a dictionary"
    assert "data" in json_data, "Response should contain 'data' key"


def test_graphql_api_extract_video_urls():
    """Test GraphQL API can extract video URLs from response"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Get tokens
    bearer_token, guest_token, query_id = get_tokens(test_url)

    # Get tweet details
    resp = get_tweet_details(test_url, guest_token, bearer_token, query_id)

    # Extract video URLs
    video_urls, gif_ptn, img_urls = create_video_urls(resp.text)

    # Verify video URLs extracted
    assert len(video_urls) > 0, "Should extract at least one video URL"
    assert all(
        url.startswith("http") for url in video_urls
    ), "All video URLs should be valid"

    # Verify gif pattern
    assert isinstance(gif_ptn, bool), "gif_ptn should be boolean"

    # Verify image URLs
    assert isinstance(img_urls, list), "img_urls should be a list"


def test_graphql_api_with_image_tweet():
    """Test GraphQL API can extract videos and images"""
    test_url = "https://x.com/tw_7rikazhexde/status/1754040936005538201"

    # Get tokens
    bearer_token, guest_token, query_id = get_tokens(test_url)

    # Get tweet details
    resp = get_tweet_details(test_url, guest_token, bearer_token, query_id)

    # Extract media
    video_urls, gif_ptn, img_urls = create_video_urls(resp.text)

    # Verify media extracted
    assert len(video_urls) > 0, "Should extract videos"
    if image_save_option:
        # Note: GraphQL API may or may not return images depending on tweet structure
        assert isinstance(img_urls, list), "img_urls should be a list"


def test_graphql_api_invalid_tweet_id():
    """Test GraphQL API handles invalid tweet ID"""
    invalid_url = "https://x.com/tw_7rikazhexde/status/invalid"

    with pytest.raises(AssertionError) as e_info:
        bearer_token, guest_token, query_id = get_tokens(invalid_url)
        get_tweet_details(invalid_url, guest_token, bearer_token, query_id)

    # Error could occur at different stages
    assert "Could not parse tweet id" in str(e_info.value) or "Failed to" in str(
        e_info.value
    )


def test_graphql_api_curl_cffi_available():
    """Test that curl-cffi is available and being used"""
    # Check if curl-cffi is imported correctly
    try:
        from curl_cffi import requests  # noqa: F401

        curl_cffi_available = True
    except ImportError:
        curl_cffi_available = False

    # curl-cffi should be available based on our implementation
    assert curl_cffi_available, "curl-cffi should be installed for GraphQL API fallback"


def test_graphql_api_dynamic_query_id():
    """Test that GraphQL API can dynamically extract query ID from main.js"""
    test_url = "https://x.com/tw_7rikazhexde/status/1650804112987136000"

    # Get tokens
    bearer_token, guest_token, query_id = get_tokens(test_url)

    # The get_tokens should return 3 values (bearer_token, guest_token, query_id)
    assert bearer_token is not None, "Bearer token should not be None"
    assert guest_token is not None, "Guest token should not be None"
    assert query_id is not None, "Query ID should not be None"

    # Query ID should be a non-empty string
    assert isinstance(query_id, str), "Query ID should be a string"
    assert len(query_id) > 0, "Query ID should not be empty"

    # get_tweet_details should use the dynamically extracted query_id
    resp = get_tweet_details(test_url, guest_token, bearer_token, query_id)
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
