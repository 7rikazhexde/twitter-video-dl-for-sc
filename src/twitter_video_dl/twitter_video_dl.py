import json
import os
import re
import subprocess
import urllib.parse

import requests

"""
Hey, thanks for reading the comments.  I love you.
Here's how this works:
1. To download a video you need a Bearer Token and a guest token.  The guest token definitely expires and the Bearer Token could, though in practice I don't think it does.
2. Use the video id get both of those as if you were an unauthenticated browser.
3. Call "TweetDetails" graphql endpoint with your tokens.
4. TweetDetails response includes a 'variants' key which is a list of video urls and details.  Find the one with the highest bitrate (bigger is better, right?) and then just download that.
5. Some videos are small.  They are contained in a single mp4 file.  Other videos are big.  They have an mp4 file that's a "container" and then a bunch of m4s files.  Once we know the name of the video file we are looking for we can look up what the m4s files are, download all of them, and then put them all together into one big file.  This currently all happens in memory.  I would guess that a very huge video might cause an out of memory error.  I don't know, I haven't tried it.
6. If it's broken, fix it yourself because I'm very slow.  Or, hey, let me know, but I might not reply for months.
"""
script_dir = os.path.dirname(os.path.realpath(__file__))
request_details_file = f"{script_dir}{os.sep}RequestDetails.json"
request_details = json.load(open(request_details_file, "r"))

features, variables = request_details["features"], request_details["variables"]

# Open setting file
with open("./src/twitter_video_dl/settings.json", "r") as f:
    data = json.load(f)

# Get the value of convert_gif_flag
convert_gif_flag = data["gif"]["convert_gif_flag"]

# Get ffmpeg loglevel
ffmpeg_loglevel = data["ffmpeg"]["loglevel"]

# Get image save option
image_save_option = data["image"]["save_option"]


def get_tokens(tweet_url):
    """
    Welcome to the world of getting a bearer token and guest id.
    1. If you request the twitter url for the tweet you'll get back a blank 'tweet not found' page.  In the browser, subsequent javascript calls will populate this page with data.  The blank page includes a script tag for a 'main.js' file that contains the bearer token.
    2. 'main.js' has a random string of numbers and letters in the filename.  We will request the tweet url, use a regex to find our unique main.js file, and then request that main.js file.
    3. The main.js file contains a bearer token.  We will extract that token and return it.  We can find the token by looking for a lot of A characters in a row.
    4. Now that we have the bearer token, how do we get the guest id?  Easy, we activate the bearer token to get it.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "TE": "trailers",
    }

    html = requests.get(tweet_url, headers=headers)

    assert (
        html.status_code == 200
    ), f"Failed to get tweet page.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {html.status_code}.  Tweet url: {tweet_url}"

    mainjs_url = re.findall(
        r"https://abs.twimg.com/responsive-web/client-web-legacy/main.[^\.]+.js",
        html.text,
    )

    assert (
        mainjs_url is not None and len(mainjs_url) > 0
    ), f"Failed to find main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}"

    mainjs_url = mainjs_url[0]
    mainjs = requests.get(mainjs_url)

    assert (
        mainjs.status_code == 200
    ), f"Failed to get main.js file.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {mainjs.status_code}.  Tweet url: {tweet_url}"

    bearer_token = re.findall(r'AAAAAAAAA[^"]+', mainjs.text)

    assert (
        bearer_token is not None and len(bearer_token) > 0
    ), f"Failed to find bearer token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {mainjs_url}"

    bearer_token = bearer_token[0]

    # get the guest token
    with requests.Session() as s:
        s.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
                "accept": "*/*",
                "accept-language": "de,en-US;q=0.7,en;q=0.3",
                "accept-encoding": "gzip, deflate, br",
                "te": "trailers",
            }
        )

        s.headers.update({"authorization": f"Bearer {bearer_token}"})

        # activate bearer token and get guest token
        guest_token = s.post("https://api.twitter.com/1.1/guest/activate.json").json()[
            "guest_token"
        ]

    assert (
        guest_token is not None
    ), f"Failed to find guest token.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}, main.js url: {mainjs_url}"

    return bearer_token, guest_token


def get_details_url(tweet_id, features, variables):
    # create a copy of variables - we don't want to modify the original
    variables = {**variables}
    variables["tweetId"] = tweet_id

    return f"https://twitter.com/i/api/graphql/0hWvDhmW8YQ-S_ib3azIrw/TweetResultByRestId?variables={urllib.parse.quote(json.dumps(variables))}&features={urllib.parse.quote(json.dumps(features))}"


def get_tweet_details(tweet_url, guest_token, bearer_token):
    tweet_id = re.findall(r"(?<=status/)\d+", tweet_url)

    assert (
        tweet_id is not None and len(tweet_id) == 1
    ), f"Could not parse tweet id from your url.  Make sure you are using the correct url.  If you are, then file a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}"

    tweet_id = tweet_id[0]

    # the url needs a url encoded version of variables and features as a query string
    url = get_details_url(tweet_id, features, variables)

    details = requests.get(
        url,
        headers={
            "authorization": f"Bearer {bearer_token}",
            "x-guest-token": guest_token,
        },
    )

    max_retries = 10
    cur_retry = 0
    while details.status_code == 400 and cur_retry < max_retries:
        try:
            error_json = json.loads(details.text)
        except json.JSONDecodeError:
            assert False, f"Failed to parse json from details error. details text: {details.text}  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {details.status_code}.  Tweet url: {tweet_url}"

        assert (
            "errors" in error_json
        ), f"Failed to find errors in details error json.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {details.status_code}.  Tweet url: {tweet_url}"

        needed_variable_pattern = re.compile(r"Variable '([^']+)'")
        needed_features_pattern = re.compile(
            r'The following features cannot be null: ([^"]+)'
        )

        for error in error_json["errors"]:
            needed_vars = needed_variable_pattern.findall(error["message"])
            for needed_var in needed_vars:
                variables[needed_var] = True

            needed_features = needed_features_pattern.findall(error["message"])
            for nf in needed_features:
                for feature in nf.split(","):
                    features[feature.strip()] = True

        url = get_details_url(tweet_id, features, variables)

        details = requests.get(
            url,
            headers={
                "authorization": f"Bearer {bearer_token}",
                "x-guest-token": guest_token,
            },
        )

        cur_retry += 1

        if details.status_code == 200:
            # save new variables
            request_details["variables"] = variables
            request_details["features"] = features

            with open(request_details_file, "w") as f:
                json.dump(request_details, f, indent=4)

    assert (
        details.status_code == 200
    ), f"Failed to get tweet details.  If you are using the correct Twitter URL this suggests a bug in the script.  Please open a GitHub issue and copy and paste this message.  Status code: {details.status_code}.  Tweet url: {tweet_url}"

    return details


def get_tweet_status_id(tweet_url):
    sid_patern = r"https://(?:x\.com|twitter\.com)/[^/]+/status/(\d+)"
    if tweet_url[len(tweet_url) - 1] != "/":
        tweet_url = tweet_url + "/"

    match = re.findall(sid_patern, tweet_url)
    if len(match) == 0:
        print("error, could not get status id from this tweet url :", tweet_url)
        exit()
    status_id = match[0]
    return status_id


def get_associated_media_id(j, tweet_url):
    sid = get_tweet_status_id(tweet_url)
    pattern = (
        r'"expanded_url"\s*:\s*"https://(?:x\.com|twitter\.com)/[^/]+/status/'
        + sid
        + r'/[^"]+",\s*"id_str"\s*:\s*"\d+",'
    )
    matches = re.findall(pattern, j)
    if len(matches) > 0:
        target = matches[0]
        target = target[0 : len(target) - 1]  # remove the coma at the end
        return json.loads("{" + target + "}")["id_str"]
    return None


def extract_mp4s(j, tweet_url, target_all_mp4s=False):
    # pattern looks like https://video.twimg.com/amplify_video/1638969830442237953/vid/1080x1920/lXSFa54mAVp7KHim.mp4?tag=16 or https://video.twimg.com/ext_tw_video/1451958820348080133/pu/vid/720x1280/GddnMJ7KszCQQFvA.mp4?tag=12
    amplitude_pattern = re.compile(
        r"(https://video.twimg.com/amplify_video/(\d+)/vid/(\d+x\d+)/[^.]+.mp4\?tag=\d+)"
    )
    ext_tw_pattern = re.compile(
        r"(https://video.twimg.com/ext_tw_video/(\d+)/pu/vid/(avc1/)?(\d+x\d+)/[^.]+.mp4\?tag=\d+)"
    )
    # format - https://video.twimg.com/tweet_video/Fvh6brqWAAQhU9p.mp4
    tweet_video_pattern = re.compile(r'https://video.twimg.com/tweet_video/[^"]+')

    # https://video.twimg.com/ext_tw_video/1451958820348080133/pu/pl/b-CiC-gZClIwXgDz.m3u8?tag=12&container=fmp4
    container_pattern = re.compile(r'https://video.twimg.com/[^"]*container=fmp4')
    media_id = get_associated_media_id(j, tweet_url)
    # find all the matches
    matches = amplitude_pattern.findall(j)
    matches += ext_tw_pattern.findall(j)
    container_matches = container_pattern.findall(j)

    tweet_video_matches = tweet_video_pattern.findall(j)

    if len(matches) == 0 and len(tweet_video_matches) > 0:
        return tweet_video_matches

    results = {}

    for match in matches:
        url, tweet_id, _, resolution = match
        if tweet_id not in results:
            results[tweet_id] = {"resolution": resolution, "url": url}
        else:
            # if we already have a higher resolution video, then don't overwrite it
            my_dims = [int(x) for x in resolution.split("x")]
            their_dims = [int(x) for x in results[tweet_id]["resolution"].split("x")]

            if my_dims[0] * my_dims[1] > their_dims[0] * their_dims[1]:
                results[tweet_id] = {"resolution": resolution, "url": url}

    if media_id:
        all_urls = []
        for twid in results:
            all_urls.append(results[twid]["url"])
        all_urls += container_matches

        url_with_media_id = []
        for url in all_urls:
            if url.__contains__(media_id):
                url_with_media_id.append(url)

        if len(url_with_media_id) > 0:
            return url_with_media_id

    if len(container_matches) > 0 and not target_all_mp4s:
        return container_matches

    if target_all_mp4s:
        urls = [x["url"] for x in results.values()]
        urls += container_matches
        return urls

    return [x["url"] for x in results.values()]


def download_parts(url, output_filename):
    resp = requests.get(url, stream=True)

    # container begins with / ends with fmp4 and has a resolution in it we want to capture
    pattern = re.compile(r"(/[^\n]*/(\d+x\d+)/[^\n]*container=fmp4)")

    matches = pattern.findall(resp.text)

    max_res = 0
    max_res_url = None

    for match in matches:
        url, resolution = match
        width, height = resolution.split("x")
        res = int(width) * int(height)
        if res > max_res:
            max_res = res
            max_res_url = url

    assert (
        max_res_url is not None
    ), f"Could not find a url to download from.  Make sure you are using the correct url.  If you are, then file a GitHub issue and copy and paste this message.  Tweet url: {url}"

    video_part_prefix = "https://video.twimg.com"

    resp = requests.get(video_part_prefix + max_res_url, stream=True)

    mp4_pattern = re.compile(r"(/[^\n]*\.mp4)")
    mp4_parts = mp4_pattern.findall(resp.text)

    assert (
        len(mp4_parts) == 1
    ), f"There should be exactly 1 mp4 container at this point.  Instead, found {len(mp4_parts)}.  Please open a GitHub issue and copy and paste this message into it.  Tweet url: {url}"

    mp4_url = video_part_prefix + mp4_parts[0]

    m4s_part_pattern = re.compile(r"(/[^\n]*\.m4s)")
    m4s_parts = m4s_part_pattern.findall(resp.text)

    with open(output_filename, "wb") as f:
        r = requests.get(mp4_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

        for part in m4s_parts:
            part_url = video_part_prefix + part
            r = requests.get(part_url, stream=True)
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

    return True


def repost_check(j, exclude_replies=True):
    # In this function, we wanna check if the tweet provided feature a reposted video.
    # If it's the case we want to get the original tweet that contains the video, in order to download it
    # In the request reply, reposted video appear like this :

    # "media_url_https": "https://pbs.twimg.com/ext_tw_video_thumb/1641074057524174848/pu/img/bu_-fjFl2k8TF9TO.jpg",
    # "source_status_id_str": "1641086559037579264",

    # Where "media_url_https" is the thumbnail url and "source_status_id_str" the status id for the original tweet (where the video is posted)
    # This is valid for all video repost, even for those in the tweet's replies.
    # That's why we have to know where the replies start in our twitter response data, to focus on the given tweet.
    # If we want to download ALL the videos below a tweet, we'll need to include replies

    try:
        # This line extract the index of the first reply
        reply_index = j.index('"conversationthread-')
    except ValueError:
        # If there are no replies we use the enrire response data length
        reply_index = len(j)
    # We truncate the response data to exclude replies
    if exclude_replies:
        j = j[0:reply_index]

    # We use this regular expression to extract the source status
    source_status_pattern = r'"source_status_id_str"\s*:\s*"\d+"'
    matches = re.findall(source_status_pattern, j)

    if len(matches) > 0 and exclude_replies:
        # We extract the source status id (ssid)
        ssid = json.loads("{" + matches[0] + "}")["source_status_id_str"]
        # We plug it in this regular expression to find expanded_url (the original tweet url)
        expanded_url_pattern = (
            r'"expanded_url"\s*:\s*"https://(?:x\.com|twitter\.com)/[^/]+/status/'
            + ssid
            + '[^"]+"'
        )
        matches2 = re.findall(expanded_url_pattern, j)

        if len(matches2) > 0:
            # We extract the url and return it
            status_url = json.loads("{" + matches2[0] + "}")["expanded_url"]
            return status_url

    if not exclude_replies:
        # If we include replies we'll have to get all ssids and remove duplicates
        ssids = []
        for match in matches:
            ssids.append(json.loads("{" + match + "}")["source_status_id_str"])
        # we remove duplicates (this line is messy but it's the easiest way to do it)
        ssids = list(set(ssids))
        if len(ssids) > 0:
            for ssid in ssids:
                expanded_url_pattern = (
                    r'"expanded_url"\s*:\s*"https://(?:x\.com|twitter\.com)/[^/]+/status/'
                    + ssid
                    + '[^"]+"'
                )
                matches2 = re.findall(expanded_url_pattern, j)
                if len(matches2) > 0:
                    status_urls = []
                    for match in matches2:
                        status_urls.append(
                            json.loads("{" + match + "}")["expanded_url"]
                        )
                    # We remove duplicates another time
                    status_urls = list(set(status_urls))
                    return status_urls

    # If we don't find source_status_id_str, the tweet doesn't feature a reposted video
    return None


def download_video(tweet_url, output_file, target_all_videos=False):
    bearer_token, guest_token = get_tokens(tweet_url)
    resp = get_tweet_details(tweet_url, guest_token, bearer_token)
    mp4s = extract_mp4s(resp.text, tweet_url, target_all_videos)
    # sometimes there will be multiple mp4s extracted.  This happens when a twitter thread has multiple videos.  What should we do?  Could get all of them, or just the first one.  I think the first one in the list is the one that the user requested... I think that's always true.  We'll just do that and change it if someone complains.
    # names = [output_file.replace('.mp4', f'_{i}.mp4') for i in range(len(mp4s))]

    if target_all_videos:
        video_counter = 1
        original_urls = repost_check(resp.text, exclude_replies=False)

        if len(original_urls) > 0:
            for url in original_urls:
                download_video(
                    url, output_file.replace(".mp4", f"_{video_counter}.mp4")
                )
                video_counter += 1
            if len(mp4s) > 0:
                for mp4 in mp4s:
                    output_file = output_file.replace(".mp4", f"_{video_counter}.mp4")
                    if "container" in mp4:
                        download_parts(mp4, output_file)

                    else:
                        # use a stream to download the file
                        r = requests.get(mp4, stream=True)
                        with open(output_file, "wb") as f:
                            for chunk in r.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                                    f.flush()
                    video_counter += 1
    else:
        original_url = repost_check(resp.text)

        if original_url:
            download_video(original_url, output_file)
        else:
            assert (
                len(mp4s) > 0
            ), f"Could not find any mp4s to download.  Make sure you are using the correct url.  If you are, then file a GitHub issue and copy and paste this message.  Tweet url: {tweet_url}"

            mp4 = mp4s[0]
            if "container" in mp4:
                download_parts(mp4, output_file)
            else:
                # use a stream to download the file
                r = requests.get(mp4, stream=True)
                with open(output_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()


def create_video_urls(json_data):
    data = json.loads(json_data)

    gif_ptn = False
    media_list = None

    try:
        media_list = data["data"]["tweetResult"]["result"]["card"]["legacy"][
            "binding_values"
        ]
    except KeyError:
        pass

    try:
        media_list = data["data"]["tweetResult"]["result"]["legacy"]["entities"][
            "media"
        ]
    except KeyError:
        pass

    if media_list is None:
        # print("non cardtype")
        try:
            media_list = data["data"]["tweetResult"]["result"]["legacy"][
                "extended_entities"
            ]["media"]
        except KeyError:
            pass

    img_urls = []
    img_urls = get_img_url(media_list)
    # get_img(img_urls, "output")

    if media_list:
        if "video_info" in media_list[0]:
            video_url_list, gif_ptn = get_non_card_type_extended_entities_vid_urls(
                media_list
            )
        elif media_list[0].get("type") == "photo":
            video_url_list, gif_ptn = get_non_card_type_entities_vid_urls(media_list)
        else:
            video_url_list = get_card_type_vid_url(media_list)
    else:
        video_url_list = []

    return video_url_list, gif_ptn, img_urls


def get_img_url(media_list):
    img_urls = []

    for media in media_list:
        media_url = media.get("media_url_https")
        if media_url.startswith("https://pbs.twimg.com/media"):
            img_urls.append(media_url)

    return img_urls


def get_img(urls, file_name):
    output_folder_path = "./output"
    os.makedirs(output_folder_path, exist_ok=True)
    num = len(urls)
    for i, url in enumerate(urls, start=1):
        if file_name == "":
            if num > 1:
                filename = f"{output_folder_path}/output_{i}"
            else:
                filename = f"{output_folder_path}/output"
        else:
            if num > 1:
                filename = f"{output_folder_path}/{file_name}_{i}"
            else:
                filename = f"{output_folder_path}/{file_name}"

        # Ask the user if the file should be overwritten if it exists
        output_file_name = f"{filename}.jpg"

        if os.path.exists(output_file_name):
            while True:
                response = (
                    input(
                        f"The file '{output_file_name}' already exists. Do you want to overwrite it? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if response == "y":
                    break
                elif response == "n":
                    print("Exit the program.")
                    return
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        with requests.get(url, stream=True) as response:
            if response.status_code == 200:
                with open(output_file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                    print(f"Image {output_file_name} downloaded successfully.")
            else:
                print(
                    f"Failed to download image from {url}. Status code: {response.status_code}"
                )
                print(
                    f"If you are using the correct Twitter URL this suggests a bug in the script. Please open a GitHub issue and copy and paste this message. Tweet url: {url}"
                )


def get_card_type_vid_url(data):
    highest_resolution_url = None
    highest_resolution_bitrate = 0
    video_url_list = []

    for item in data:
        value = item.get("value")
        if value and value.get("string_value"):
            string_value = value["string_value"]
            try:
                json_value = json.loads(string_value)
                media_entities = json_value.get("media_entities")
                if media_entities:
                    for media_key, media_info in media_entities.items():
                        video_info = media_info.get("video_info")
                        if video_info:
                            variants = video_info.get("variants")
                            if variants:
                                for variant in variants:
                                    content_type = variant.get("content_type")
                                    if content_type == "video/mp4":
                                        bitrate = variant.get("bitrate", 0)
                                        if bitrate > highest_resolution_bitrate:
                                            highest_resolution_bitrate = bitrate
                                            highest_resolution_url = variant["url"]
            except json.JSONDecodeError:
                continue

    if highest_resolution_url:
        video_url_list.append(highest_resolution_url)

    return video_url_list


def get_non_card_type_entities_vid_urls(media_list):
    video_url_list = []
    gif_ptn = False

    if media_list:
        for media_item in media_list:
            video_info = media_item.get("video_info")
            if not video_info:
                continue

            variants = video_info.get("variants")
            if not variants:
                continue

            video_url = None
            max_bitrate = 0

            for variant in variants:
                if variant.get("bitrate") and variant["bitrate"] > max_bitrate:
                    max_bitrate = variant["bitrate"]
                    video_url = variant["url"]
                elif variant.get("bitrate") == 0:  # gif case
                    video_url = variant["url"]
                    gif_ptn = True

            if video_url:
                video_url_list.append(video_url)
    return video_url_list, gif_ptn


def get_non_card_type_extended_entities_vid_urls(media_list):
    video_url_list = []
    gif_ptn = False

    if media_list:
        for media_item in media_list:
            video_info = media_item.get("video_info")
            if not video_info:
                continue

            variants = video_info.get("variants")
            if not variants:
                continue

            video_url = None
            max_bitrate = 0

            for variant in variants:
                if variant.get("bitrate") and variant["bitrate"] > max_bitrate:
                    max_bitrate = variant["bitrate"]
                    video_url = variant["url"]
                elif variant.get("bitrate") == 0:  # gif case
                    video_url = variant["url"]
                    gif_ptn = True

            if video_url:
                video_url_list.append(video_url)
    return video_url_list, gif_ptn


def download_videos(video_urls, output_file, output_folder_path, gif_ptn):
    os.makedirs(output_folder_path, exist_ok=True)
    num = len(video_urls)

    for i, video_url in enumerate(video_urls, start=1):
        if output_file == "":
            if num > 1:
                filename = f"{output_folder_path}/output_{i}"
            else:
                filename = f"{output_folder_path}/output"
        else:
            if num > 1:
                filename = f"{output_folder_path}/{output_file}_{i}"
            else:
                filename = f"{output_folder_path}/{output_file}"

        # Ask the user if the file should be overwritten if it exists
        output_file_name = f"{filename}.mp4"
        if os.path.exists(output_file_name):
            while True:
                response = (
                    input(
                        f"The file '{output_file_name}' already exists. Do you want to overwrite it? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if response == "y":
                    break
                elif response == "n":
                    print("Exit the program.")
                    return
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        with requests.get(video_url, stream=True) as response:
            if response.status_code == 200:
                with open(output_file_name, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                    print(f"Video {output_file_name} downloaded successfully.")
            else:
                print(
                    f"Failed to download video from {video_url}. Status code: {response.status_code}"
                )
                print(
                    f"If you are using the correct Twitter URL this suggests a bug in the script. Please open a GitHub issue and copy and paste this message. Tweet url: {video_url}"
                )

        if gif_ptn:
            # Covert mp4 to gif
            if convert_gif_flag:
                command = [
                    "ffmpeg",
                    "-i",
                    f"{filename}.mp4",
                    f"{filename}.gif",
                    "-loglevel",
                    ffmpeg_loglevel,
                ]
                subprocess.run(command)
                # Delete mp4 after creating gif file
                subprocess.run(["rm", f"{filename}.mp4"])
                print(f"Video Convert Success(mp4 to gif): {filename}.gif")
    if image_save_option:
        print("All videos(gifs) & images downloaded successfully.")
    else:
        print("All videos(gifs) downloaded successfully.")


def download_video_for_sc(tweet_url, output_file="", output_folder_path="./output"):
    bearer_token, guest_token = get_tokens(tweet_url)
    resp = get_tweet_details(tweet_url, guest_token, bearer_token)
    video_urls, gif_ptn, img_urls = create_video_urls(resp.text)
    if image_save_option:
        get_img(img_urls, output_file)
    download_videos(video_urls, output_file, output_folder_path, gif_ptn)
