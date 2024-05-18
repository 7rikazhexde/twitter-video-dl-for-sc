# twitter-video-dl-for-sc

This project is based on the original code of the [inteoryx / twitter-video-dl](https://github.com/inteoryx/twitter-video-dl) project, which allows users to download X(Twitter) App videos as MP4 files using Python, FFmpeg and URLs without the need for API keys. I forked this project for use in iOS Shortcuts application.

## ⚠️ Notice
Currently, the latest changes have not been reflected in the [master/main](https://github.com/7rikazhexde/twitter-video-dl-for-sc/tree/main) branch of this project.  
Please use the [dev_bug_16](https://github.com/7rikazhexde/twitter-video-dl-for-sc/tree/dev_bug_16) branch instead. The [dev_bug_16](https://github.com/7rikazhexde/twitter-video-dl-for-sc/tree/dev_bug_16) branch contains bug fixes for Issue [#16](https://github.com/7rikazhexde/twitter-video-dl-for-sc/issues/16).  
I'm temporarily managing the code in this branch to address changes in X(formerly Twitter) specifications.

## ToC

- [twitter-video-dl-for-sc](#twitter-video-dl-for-sc)
  - [⚠️ Notice](#️-notice)
  - [ToC](#toc)
  - [Demo (Shortcuts)](#demo-shortcuts)
  - [Demo (Shortcuts for Mac Browser)](#demo-shortcuts-for-mac-browser)
  - [Demo (Browser Extension)](#demo-browser-extension)
  - [Usage](#usage)
    - [Installing FFmpeg](#installing-ffmpeg)
    - [For Shortcuts](#for-shortcuts)
  - [For Mac Browser](#for-mac-browser)
  - [For Browser Extension](#for-browser-extension)
  - [CLI For Windows / Mac / Linux](#cli-for-windows--mac--linux)
  - [Auto Retry Feature](#auto-retry-feature)
  - [Other](#other)
  - [Test-Environment For twitter-video-dl-for-sc](#test-environment-for-twitter-video-dl-for-sc)
    - [Usage](#usage-1)

## Demo (Shortcuts)

|One video per post|Mixing images and videos in one post(*1)|Mixing images and videos in a thread(*1)|
|:---:|:---:|:---:|
|<img src="./demo/demo1_v1_30fps_400x866.gif" width="80%" alt="One video per post">|<img src="./demo/demo2_v1_30fps_400x866.gif" width="80%" alt="Mixing images and videos in one post">|<img src="./demo/demo3_v3_30fps_400x866.gif" width="80%" alt="Mixing images and videos in a thread">|
|[Original Post Link(Media)](https://x.com/tw_7rikazhexde/status/1650804112987136000?s=20)|[Original Post Link(Media)](https://twitter.com/tw_7rikazhexde/status/1650808610157662211?s=20)|[Original Post Link(Media)](https://x.com/tw_7rikazhexde/status/1754040936005538201?s=20)|

(*1): If the `"save_option"` of the `"image"` key defined in [settings.json](./src/twitter_video_dl/settings.json) is `true`, the video and image are saved; if `false`, only the video is saved.

## Demo (Shortcuts for Mac Browser)

<img src="./demo/demo1_twitter-video-dl-sc-for-mac_30fps_1440x900.gif" alt="twitter-video-dl-sc-for-mac demo">

## Demo (Browser Extension)

<img src="./demo/demo1_twitter-video-dl-sc-for-server_30fps_2880x1800.gif" alt="twitter-video-dl-sc-for-server demo">

## Usage

### Installing FFmpeg

> [!NOTE]
> **- Use the ffmpeg command to save GIF files.**  
> **- GIF files are converted from MP4 files; if you do not need to save GIF files, set `"convert_gif_flag": false` in `settings.json`.**  
> **- For shortcuts, the a-Shell application used supports ffmpeg, so installation is not necessary.**  
> **- The actual version information displayed below may vary from one system to another; but if a message such as ffmpeg: command not found appears instead of the version information, FFmpeg is not properly installed.**

In order to execute the code, FFmpeg must be installed and accessible via the $PATH environment variable.

There are a variety of ways to install FFmpeg, such as the official download links, or using your package manager of choice (e.g. sudo apt install ffmpeg on Debian/Ubuntu, brew install ffmpeg on OS X, etc.).

Regardless of how FFmpeg is installed, you can check if your environment path is set correctly by running the ffmpeg command from the terminal, in which case the version information should appear, as in the following example (truncated for brevity):

```bash
ffmpeg
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
  built with Apple clang version 14.0.3 (clang-1403.0.22.14.1)
```

### For Shortcuts

> [!NOTE]
> **- Currently only Japanese language support is available.**  
> **- It has been tested on iPhone and iPad, but not on Mac.**  
> **- Please note that the shortcuts used are different for iPhone, iPad and Mac.**  

> [!Important]
> **Be sure to review the notes, limitations, and comments in the comments when performing shortcuts.**  

1. Download [Shortcuts](https://apps.apple.com/us/app/shortcuts/id915249334) and [a-Shell](https://apps.apple.com/jp/app/a-shell/id1473805438) from the AppStore
2. Add Shortcut to save Twitter videos
   - twitter-video-dl-sc setup ([iCloud Link](https://www.icloud.com/shortcuts/a6adf3692039454a8168f7221b808c67))
   - twitter-video-dl-sc ([iCloud Link](https://www.icloud.com/shortcuts/ecbc62aa449c4e2cb4fea1e8eec9d168))
3. Run the ***twitter-video-dl-sc setup*** setup shortcut  
   - DL [git](https://github.com/holzschu/a-Shell-commands/releases/download/0.1/git) command from [a-Shell-commands](https://github.com/holzschu/a-Shell-commands)
   - git clone [twitter-video-dl-for-sc](https://github.com/7rikazhexde/twitter-video-dl-for-sc)  
4. Run the ***twitter-video-dl-sc*** from a Twitter share ([See demo video](#demo-shortcuts))  
   - If you do not specify an output file name, the file name is after the user _ id in the URL.
   - Replace '/' with '-' in the file name and new line ith '_'.

## For Mac Browser

Only differences from the procedure for iPhone and iPad are described.

1. Add Shortcut to save Twitter videos
   - twitter-video-dl-sc setup ([iCloud Link](https://www.icloud.com/shortcuts/a6adf3692039454a8168f7221b808c67))
   - twitter-video-dl-sc-for-mac-browser ([iCloud Link](https://www.icloud.com/shortcuts/bfbf5cd42dbe40cba7ed60f066be850d))

2. When executing the shortcut, start **the video-posted post in the browser** that you start on your Mac, and then execute ***twitter-video-dl-sc-for-mac-browser*** from the tab Sharing. If it saves successfully, the destination will be displayed. ([See demo video](#demo-shortcuts-for-mac-browser))

## For Browser Extension

> [!WARNING]
> **Browsers that have been tested are chrome and brave.**

> [!NOTE]
> **Please check [See demo video](#demo-browser-extension)**

1. extensions > load unpackaged extensions > Local Package
   **[twitter-video-dl-send](./browser_extension/twitter-video-dl-send/)**
2. Start the server (`poetry run python twitter-video-dl-server.py`)
3. Open the X(Twitter) web page where the video was posted.
4. Specify the filename and URL (not required) in the extension and run the process of saving the video
5. If there are no errors, the video will be saved in the **output** folder

## CLI For Windows / Mac / Linux

> [!NOTE]
> **[Partially the same as twitter-video-dl and depends on it.](https://github.com/inteoryx/twitter-video-dl)**  

1. Clone the repo and pip install -r requirements.txt (just the requests library)
2. See a video on twitter that you want to save.
3. Invoke the script, e.g.:

```bash
# File name specified
python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 output_file_name
```

```bash
# Without file name
python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 ""
```

Done, now you should have an mp4 file of the highest bitrate version of that video available.

## Auto Retry Feature

> [!NOTE]
> **[Same as twitter-video-dl and depends on it.](https://github.com/inteoryx/twitter-video-dl)**  

From time to time, every week or so, Twitter will add some new request parameters that they expect from callers asking for their content.  Twitter refers to these as "features" or "variables".  The twitter-video-dl script will try to detect when a new feature or variable has been added and automatically accommodate the new element.  This is not foolproof though.  It's possible the script will fail with an error message.  If it does, please open an issue (or send a PR).

## Other

> [!NOTE]
> **[Same as twitter-video-dl and depends on it.](https://github.com/inteoryx/twitter-video-dl)**  

I have tested this with the 10 video files listed in test_videos.txt and it seems to work.  Highly possible there are other variants out there that this won't work for.  If you encounter such, please submit an issue and include the URL that doesn't work.  If the script doesn't work double check you have the URL right.

## Test-Environment For twitter-video-dl-for-sc

twitter-video-dl-for-sc uses ffmpeg for saving videos. Therefore, we provide a test environment for twitter-video-dl-for-sc in addition to the test cases for twitter-video-dl.

### Usage

If you get an error with the specified URL, please register an issue. If you want to test individually, you can test in advance by adding the URL of the post where the video was posted to [test_data.toml](./tests/test_data.toml).

> [!NOTE]
> **- The test environment depends on **pytest**, which is added as part of the dev environment dependency files with the `poetry install` command.**  
> **- You can run the test command in `poetry run pytest --html=pytest-html/report.html`.**
