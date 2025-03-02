import re

import requests


def get_tokens(tweet_url):
    """
    Updated function to extract bearer token and guest token from Twitter/X page
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "en-US, en, *;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "TE": "trailers",
    }

    session = requests.Session()

    # First, try to get the page
    response = session.get(tweet_url, headers=headers)

    # Check for meta refresh redirect
    meta_redirect_match = re.search(
        r'<meta\s+http-equiv="refresh"\s+content="0;\s*url=([^"]+)"',
        response.text,
        re.IGNORECASE,
    )

    # Check for JavaScript redirect
    js_redirect_match = re.search(
        r'window\.location\.replace\("([^"]+)"\)', response.text
    )

    # Decide which redirect to use
    redirect_url = None
    if meta_redirect_match:
        redirect_url = meta_redirect_match.group(1)
    elif js_redirect_match:
        redirect_url = js_redirect_match.group(1)

    # If no redirect found, use the original URL
    if not redirect_url:
        redirect_url = tweet_url

    print(f"Redirect URL: {redirect_url}")

    # Follow the redirect
    response = session.get(redirect_url, headers=headers)

    # Find main.js URL
    mainjs_urls = re.findall(
        r"https://abs\.twimg\.com/responsive-web/client-web-legacy/main\.[^\.]+\.js",
        response.text,
    )

    if not mainjs_urls:
        raise ValueError(f"No main.js URLs found. URL: {redirect_url}")

    mainjs_url = mainjs_urls[0]
    print(f"Main.js URL: {mainjs_url}")

    # Fetch main.js
    mainjs = session.get(mainjs_url)

    # Extract bearer token
    bearer_tokens = re.findall(r'AAAAAAAAA[^"]+', mainjs.text)

    if not bearer_tokens:
        raise ValueError(f"No bearer tokens found in main.js. URL: {mainjs_url}")

    bearer_token = bearer_tokens[0]

    # Activate guest token
    session.headers.update({"authorization": f"Bearer {bearer_token}"})
    guest_token_response = session.post(
        "https://api.twitter.com/1.1/guest/activate.json"
    )

    if guest_token_response.status_code != 200:
        raise ValueError(
            f"Failed to activate guest token. Status: {guest_token_response.status_code}"
        )

    guest_token = guest_token_response.json()["guest_token"]

    return bearer_token, guest_token


# Example usage
if __name__ == "__main__":
    tweet_url = "https://twitter.com/i/status/1650804112987136000"
    try:
        bearer_token, guest_token = get_tokens(tweet_url)
        print(f"Bearer Token: {bearer_token}")
        print(f"Guest Token: {guest_token}")
    except Exception as e:
        print(f"Error: {e}")
