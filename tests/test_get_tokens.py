import pytest

# Response class is a class for representing HTTP response and is used to hold information such as status code, header, and body.
from requests.models import Response

from src.twitter_video_dl.twitter_video_dl import get_tokens


def test_get_tokens_url_gres_404(mocker):
    """Test function for the first get request to be executed (other than OK)

    Args:
        mocker

    Returns:
        None

    Note:
        Set an empty byte string to the _content attribute of the Response object.
        The _content attribute holds the body of the HTTP response.
        Normally, this attribute is set to the body of the response returned from the server when a method such as requests.get is called.
        However, in this test code, the HTTP request is not actually made, but the Response object is created directly, so the _content attribute is set manually.

    """
    # Set URL for testing
    tweet_url = "http://test.com"

    # Set response to return status code other than 200
    response = Response()
    response.status_code = 404

    # Mock requests.get and set it to return the response you created
    mocker.patch("requests.get", return_value=response)

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to get tweet page.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {response.status_code}.  Tweet url: {tweet_url}"
    )


def test_get_tokens_url_gres_200(mocker):
    """Test function for the first get request to be executed (OK)"""
    # Set URL for testing
    tweet_url = "http://test.com"

    # Set response to return status code 200
    response = Response()
    response.status_code = 200
    # response._content = b''
    response._content = b"<html></html>"

    # Mock requests.get and set it to return the response you created
    mocker.patch("requests.get", return_value=response)

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to find main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}"
    )


def test_get_tokens_url_gres_200_mainjs_gres_404(mocker):
    """Test function for get requests to mainjs (other than OK)"""
    # Set URL for testing
    tweet_url = "http://test.com"

    # Create a response that returns status code 200
    response = Response()
    response.status_code = 200
    response._content = b"https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"  # main.jsのURLを含むHTMLを設定します

    # Create response to main.js URL
    mainjs_response = Response()
    # Set status code other than 200
    mainjs_response.status_code = 404

    # Mock requests.get and set it to return the response you created
    mocker.patch("requests.get", side_effect=[response, mainjs_response])

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to get main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {mainjs_response.status_code}.  Tweet url: {tweet_url}"
    )


def test_get_tokens_url_gres_200_mainjs_gres_200_ng(mocker):
    """Test function for get requests to mainjs (other than OK)"""
    # Set URL for testing
    tweet_url = "http://test.com"

    # Create a response that returns status code 200
    response = Response()
    response.status_code = 200
    response._content = b"https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"  # main.jsのURLを含むHTMLを設定します
    response.url = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )

    # Create response to main.js URL
    mainjs_response = Response()
    mainjs_response.status_code = 200
    mainjs_response._content = b"bbbbbbbb"

    # Mock requests.get and set it to return the response you created
    mocker.patch("requests.get", side_effect=[response, mainjs_response])

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to find bearer token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {response.url}"
    )


def test_get_tokens_guest_token_null_ptn1(mocker):
    # Test function for cases where guest_token cannot be obtained
    # Set URL for testing
    tweet_url = "http://test.com"

    # Create a response that returns status code 200
    response = Response()
    response.status_code = 200
    # Set HTML including main.js URL
    response._content = (
        b"https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )
    response.url = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )

    # Create response to main.js URL
    mainjs_response = Response()
    mainjs_response.status_code = 200
    # Set HTML containing bearer_token
    mainjs_response._content = b"AAAAAAAAAabc123"

    # Create response to get guest_token
    guest_token_response = Response()
    # Set JSON containing guest_token
    guest_token_response._content = b'{"guest_token": null}'

    # Mock requests.get and requests.Session.post and set them to return the created response
    mocker.patch("requests.get", side_effect=[response, mainjs_response])
    mocker.patch("requests.Session.post", return_value=guest_token_response)

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to find guest token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {response.url}"
    )


def test_get_tokens_guest_token_null_ptn2(mocker):
    """Test function for cases where guest_token cannot be obtained"""
    # Set URL for testing
    tweet_url = "http://test.com"

    # Create a response that returns status code 200
    response = mocker.Mock()
    response.status_code = 200
    # Set HTML including main.js URL
    response.text = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )
    response.url = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )

    # Create response to main.js URL
    mainjs_response = mocker.Mock()
    mainjs_response.status_code = 200
    # Set HTML containing bearer_token
    mainjs_response.text = "AAAAAAAAAabc123"

    # Create response to get guest_token
    guest_token_response = mocker.Mock()
    # Set JSON containing guest_token
    guest_token_response.json.return_value = {"guest_token": None}

    # Mock requests.get and requests.Session.post and set them to return the created response
    mocker.patch("requests.get", side_effect=[response, mainjs_response])
    mocker.patch("requests.Session.post", return_value=guest_token_response)

    # Call get_tokens function and check expected result
    with pytest.raises(AssertionError) as e:
        get_tokens(tweet_url)
    assert (
        str(e.value)
        == f"Failed to find guest token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {response.url}"
    )


def test_get_tokens_ok(mocker):
    """Normal test function of get_tokens function"""
    # Set URL for testing
    tweet_url = "http://test.com"

    # Create a response that returns status code 200
    response = mocker.Mock()
    response.status_code = 200
    # Set HTML including main.js URL
    response.text = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )
    response.url = (
        "https://abs.twimg.com/responsive-web/client-web-legacy/main.abc123.js"
    )

    # Create response to main.js URL
    mainjs_response = mocker.Mock()
    mainjs_response.status_code = 200
    # Set HTML containing bearer_token
    mainjs_response.text = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    # Create response to get guest_token
    guest_token_response = mocker.Mock()
    # Set JSON containing guest_token
    guest_token_response.json.return_value = {"guest_token": "1735631202730848507"}

    # Mock requests.get and requests.Session.post and set them to return the created response
    mocker.patch("requests.get", side_effect=[response, mainjs_response])
    mocker.patch("requests.Session.post", return_value=guest_token_response)

    # Call get_tokens function and check expected result
    bearer_token, guest_token = get_tokens(tweet_url)
    assert (
        bearer_token
        == "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )
    assert guest_token == "1735631202730848507"
