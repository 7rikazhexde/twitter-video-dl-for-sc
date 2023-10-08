import argparse

import src.twitter_video_dl.twitter_video_dl as tvdl

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a video from a twitter url and save it as a local mp4 file."
    )

    parser.add_argument(
        "twitter_url",
        type=str,
        help="Twitter URL to download.  e.g. https://x.com/tw_7rikazhexde/status/1710868951109124552?s=20",
    )

    parser.add_argument(
        "file_name",
        type=str,
        help="Save twitter video to this filename. e.g. twittervid.mp4",
    )

    args = parser.parse_args()

    file_name = args.file_name

    tvdl.download_video_for_sc(args.twitter_url, args.file_name)
