# twitter-video-dl-for-sc

This project is based on the original code of the [inteoryx / twitter-video-dl](https://github.com/inteoryx/twitter-video-dl) project, which allows users to download X(Twitter) App videos as MP4 files using Python, FFmpeg and URLs without the need for API keys. I forked this project for use in iOS Shortcuts application.

**Key Features:**

- **Dual-API Strategy**: Uses Syndication API (primary, no authentication required) with GraphQL API fallback for maximum reliability
- **Card-Type Video Support**: Downloads videos from promoted/ad tweets
- **iOS Shortcuts Integration**: Optimized for iOS Shortcuts workflow
- **Browser Extension Support**: Chrome/Brave extension for easy video downloads
- **GIF Conversion**: Automatic MP4 to GIF conversion using FFmpeg

## ToC

- [twitter-video-dl-for-sc](#twitter-video-dl-for-sc)
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
  - [Development](#development)
    - [Prerequisites](#prerequisites)
    - [Setup Development Environment](#setup-development-environment)
      - [Option 1: Using uv (Recommended)](#option-1-using-uv-recommended)
      - [Option 2: Using pip and venv](#option-2-using-pip-and-venv)
    - [Development Commands](#development-commands)
  - [API Approach \& Auto Retry Feature](#api-approach--auto-retry-feature)
    - [Dual-API Strategy](#dual-api-strategy)
    - [Auto Retry Feature](#auto-retry-feature)
  - [Supported Tweet Types](#supported-tweet-types)
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

### For Mac Browser

Only differences from the procedure for iPhone and iPad are described.

1. Add Shortcut to save Twitter videos
   - twitter-video-dl-sc setup ([iCloud Link](https://www.icloud.com/shortcuts/a6adf3692039454a8168f7221b808c67))
   - twitter-video-dl-sc-for-mac-browser ([iCloud Link](https://www.icloud.com/shortcuts/bfbf5cd42dbe40cba7ed60f066be850d))

2. When executing the shortcut, start **the video-posted post in the browser** that you start on your Mac, and then execute ***twitter-video-dl-sc-for-mac-browser*** from the tab Sharing. If it saves successfully, the destination will be displayed. ([See demo video](#demo-shortcuts-for-mac-browser))

### For Browser Extension

> [!WARNING]
> **Browsers that have been tested are chrome and brave.**

> [!NOTE]
> **Please check [See demo video](#demo-browser-extension)**

1. extensions > load unpackaged extensions > Local Package
   **[twitter-video-dl-send](./browser_extension/twitter-video-dl-send/)**
2. Start the server
   - **With uv**: `uv run python twitter-video-dl-server.py`
   - **Without uv**: `python twitter-video-dl-server.py`
3. Open the X(Twitter) web page where the video was posted.
4. Specify the filename and URL (not required) in the extension and run the process of saving the video
5. If there are no errors, the video will be saved in the **output** folder

### CLI For Windows / Mac / Linux

> [!NOTE]
> **[Partially the same as twitter-video-dl and depends on it.](https://github.com/inteoryx/twitter-video-dl)**  

<details>
<summary><b>Option 1: Using uv (Recommended)</b></summary>

1. Clone the repo and install dependencies:

   ```bash
   # Clone the repository
   git clone https://github.com/7rikazhexde/twitter-video-dl-for-sc.git
   cd twitter-video-dl-for-sc

   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync
   ```

2. See a video on twitter that you want to save.

3. Invoke the script, e.g.:

   ```bash
   # File name specified
   uv run python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 output_file_name
   ```

   ```bash
   # Without file name
   uv run python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 ""
   ```

</details>

<details>
<summary><b>Option 2: Using pip and venv</b></summary>

1. Clone the repo and install dependencies:

   ```bash
   # Clone the repository
   git clone https://github.com/7rikazhexde/twitter-video-dl-for-sc.git
   cd twitter-video-dl-for-sc

   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

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

</details>

Done, now you should have an mp4 file of the highest bitrate version of that video available.

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [just](https://github.com/casey/just) as a command runner.

### Prerequisites

- Python 3.11 or higher
- FFmpeg (for video processing)
- **Recommended**: [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- **Optional**: [just](https://github.com/casey/just) - Command runner

### Setup Development Environment

#### Option 1: Using uv (Recommended)

1. **Install uv**:

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or with pip
   pip install uv
   ```

2. **Install just** (optional, but recommended):

   ```bash
   # macOS
   brew install just

   # Linux
   curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin

   # Or with cargo
   cargo install just
   ```

3. **Setup the project**:

   ```bash
   # Clone the repository
   git clone https://github.com/7rikazhexde/twitter-video-dl-for-sc.git
   cd twitter-video-dl-for-sc

   # If you have just installed
   just setup

   # Or manually with uv
   uv sync --extra dev
   uv run pre-commit install
   ```

#### Option 2: Using pip and venv

1. **Clone the repository**:

   ```bash
   git clone https://github.com/7rikazhexde/twitter-video-dl-for-sc.git
   cd twitter-video-dl-for-sc
   ```

2. **Create and activate virtual environment**:

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows:
   # .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   # Install development dependencies
   pip install -r requirements-dev.txt

   # Install pre-commit hooks
   pre-commit install
   ```

### Development Commands

<details>
<summary><b>Using just (with uv)</b></summary>

If you have `just` installed, you can use these convenient commands:

```bash
# Show all available commands
just

# Code quality checks
just ruffcheck          # Check code with ruff
just rufffix            # Fix code issues automatically
just format             # Format code

# Testing
just test               # Run tests

# Environment management
just install            # Install all dependencies
just update             # Update dependencies
just show-outdated      # Check for outdated packages
just clean              # Clean up generated files

# Pre-commit hooks
just pre-commit         # Run pre-commit hooks on all files

# Version management
just update-version 0.2.12        # Update version
just prepare-release 0.2.12       # Prepare for release

# Debug
just debug-info         # Show debug information
just help               # Show detailed help
```

</details>

<details>
<summary><b>Using uv directly (without just)</b></summary>

If you don't have `just` installed, you can use `uv` directly:

```bash
# Code quality
uv run ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci
uv run ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci --fix
uv run ruff format twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci

# Testing
uv run pytest tests/

# Pre-commit
uv run pre-commit run --all-files

# Update dependencies
uv lock --upgrade
uv sync --extra dev
```

</details>

<details>
<summary><b>Using pip and venv (without uv)</b></summary>

If you're using traditional pip and venv setup:

```bash
# Activate virtual environment first (if not already activated)
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Code quality
ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci
ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci --fix
ruff format twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci

# Testing
pytest tests/

# Pre-commit
pre-commit run --all-files

# Update dependencies
pip install --upgrade -r requirements-dev.txt
```

</details>

## API Approach & Auto Retry Feature

### Dual-API Strategy

This project uses a two-tier API approach for maximum reliability:

1. **Syndication API (Primary)**
   - Endpoint: `cdn.syndication.twimg.com`
   - No authentication required
   - More stable and reliable
   - Supports regular videos, GIFs, and card-type videos (promoted/ad tweets)

2. **GraphQL API (Fallback)**
   - Endpoint: `api.x.com/i/api/graphql`
   - Used when Syndication API fails
   - Requires bearer token and guest token
   - Dynamic Query ID extraction from main.js

### Auto Retry Feature

> [!NOTE]
> **This feature applies to the GraphQL API fallback method.**

From time to time, every week or so, Twitter will add some new request parameters that they expect from callers asking for their content. Twitter refers to these as "features" or "variables". The twitter-video-dl script will try to detect when a new feature or variable has been added and automatically accommodate the new element. This is not foolproof though. It's possible the script will fail with an error message. If it does, please open an issue (or send a PR).

## Supported Tweet Types

This application has been tested with the following tweet types:

- ✅ **Regular videos** (2019-2024)
- ✅ **GIF animations**
- ✅ **Mixed media** (images + videos)
- ✅ **Card-type videos** (promoted/ad tweets)
- ✅ **Thread videos** (multiple videos in a thread)

All 17 test cases pass successfully. If you encounter a URL that doesn't work, please submit an issue and include:

- The URL that doesn't work
- The error message (if any)
- Your environment (OS, Python version, etc.)

Before submitting an issue, please double-check that you have the correct URL format.

## Test-Environment For twitter-video-dl-for-sc

twitter-video-dl-for-sc uses ffmpeg for saving videos. Therefore, we provide a test environment for twitter-video-dl-for-sc in addition to the test cases for twitter-video-dl.

### Usage

If you get an error with the specified URL, please register an issue. If you want to test individually, you can test in advance by adding the URL of the post where the video was posted to [test_data.toml](./tests/test_data.toml).

> [!NOTE]
> **Testing with uv**: `uv sync --extra dev` then `uv run pytest` or `just test`  
> **Testing with pip**: `pip install -r requirements-dev.txt` then `pytest tests/`

> [!IMPORTANT]
> When running full tests with `just test`, ensure that the `"save_option"` of the `"image"` key in [settings.json](./src/twitter_video_dl/settings.json) is set to `true`.
