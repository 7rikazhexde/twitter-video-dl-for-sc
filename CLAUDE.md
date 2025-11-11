# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that downloads X (Twitter) videos as MP4 files without requiring API keys. It's forked from `inteoryx/twitter-video-dl` and adapted specifically for iOS Shortcuts integration, with additional features for images, GIFs, and browser extension support.

**Key differentiators from upstream:**

- iOS Shortcuts integration (primary use case)
- Mac browser extension support
- Chrome/Brave browser extension support
- Image downloading alongside videos (configurable)
- GIF conversion using FFmpeg
- Settings configuration via `src/twitter_video_dl/settings.json`

## Development Commands

### Using uv + just (Recommended)

```bash
just setup              # Setup development environment
just ruffcheck          # Check code with ruff
just rufffix            # Fix code issues automatically
just format             # Format code
just test               # Run tests (requires settings.json image.save_option=true)
just pre-commit         # Run pre-commit hooks
just update             # Update dependencies
just prepare-release 0.2.13  # Prepare for release
```

### Using uv directly

```bash
uv sync --extra dev                                           # Install dependencies
uv run ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci --fix
uv run ruff format twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci
uv run pytest tests/
uv run pre-commit run --all-files
```

### Using pip + venv

```bash
source .venv/bin/activate  # Activate venv first
ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci --fix
ruff format twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci
pytest tests/
```

### Running the application

```bash
# With uv (recommended)
uv run python twitter-video-dl-for-sc.py <TWEET_URL> <OUTPUT_FILENAME>

# With filename
uv run python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 my_video

# Without filename (auto-generated)
uv run python twitter-video-dl-for-sc.py https://twitter.com/i/status/1650804112987136000 ""
```

### Server mode (for browser extension)

```bash
uv run python twitter-video-dl-server.py
```

## Architecture

### Core Module Structure

```bash
src/twitter_video_dl/
├── twitter_video_dl.py    # Core video download logic
├── settings.json          # Configuration (gif, ffmpeg, image, debug)
└── RequestDetails.json    # Twitter API features/variables (auto-updated)
```

### Entry Points

1. **CLI**: `twitter-video-dl-for-sc.py` - Main CLI entry point
2. **Server**: `twitter-video-dl-server.py` - HTTP server for browser extension
3. **Legacy CLI**: `twitter-video-dl.py` - Wrapper for original functionality

### API Approach

The application uses a dual-API strategy for maximum reliability:

1. **Syndication API (Primary)**: `cdn.syndication.twimg.com`
   - No authentication required
   - More stable and reliable
   - Supports regular videos, GIFs, and card-type videos (promoted/ad tweets)

2. **GraphQL API (Fallback)**: `api.x.com/i/api/graphql`
   - Used when Syndication API fails
   - Requires bearer token and guest token
   - Dynamic Query ID extraction from main.js

### Key Functions in `twitter_video_dl.py`

**Syndication API (Primary Method):**

- `get_tweet_details_syndication(tweet_url)`: Fetches tweet data using Syndication API (no auth required)
- `extract_media_from_syndication(syndication_data)`: Extracts video/image URLs from Syndication API response
  - Supports regular videos from `mediaDetails`
  - Supports card-type videos from `card.binding_values.unified_card` (promoted/ad tweets)

**GraphQL API (Fallback Method):**

- `get_tokens(tweet_url)`: Extracts bearer token from main.js and guest token from HTML cookies, dynamically gets GraphQL Query ID
- `get_tweet_details(tweet_url, guest_token, bearer_token, query_id)`: Calls TweetResultByRestId GraphQL endpoint
- `create_video_urls(json_data)`: Parses GraphQL response JSON to extract video/image URLs

**Common Functions:**

- `download_video_for_sc(tweet_url, output_file, output_folder_path)`: Main entry point for shortcuts (tries Syndication API first, falls back to GraphQL)
- `download_videos(video_urls, ...)`: Downloads videos with optional GIF conversion via FFmpeg
- `get_img(urls, ...)`: Downloads images if `image.save_option` is enabled

### Auto-Retry Mechanism (GraphQL API Fallback)

The `get_tweet_details()` function includes smart retry logic (max 10 attempts) that:

- Detects missing Twitter API "features" or "variables" from 400 errors
- Automatically adds required parameters to the request
- Updates `RequestDetails.json` on successful retry
- This handles Twitter's frequent API parameter changes

### Configuration (`settings.json`)

```json
{
  "gif": {
    "convert_gif_flag": true    // Convert MP4 to GIF for animated tweets
  },
  "ffmpeg": {
    "loglevel": "error"         // FFmpeg verbosity
  },
  "image": {
    "save_option": true         // Save images alongside videos
  },
  "debug_option": true          // Write debug.log
}
```

**Important**: When running `just test`, ensure `image.save_option` is `true` for full test coverage.

### Video Download Flow

**Primary Flow (Syndication API):**

1. Parse tweet URL to extract status ID
2. Fetch tweet data from Syndication API (`cdn.syndication.twimg.com/tweet-result?id={tweet_id}`)
3. Extract video URLs from response:
   - Regular videos: from `mediaDetails` array
   - Card-type videos: from `card.binding_values.unified_card.string_value` (promoted/ad tweets)
4. Select highest bitrate variant
5. Download video file
6. Optional: Convert MP4 to GIF for animated tweets
7. Optional: Download associated images

**Fallback Flow (GraphQL API):**

Used when Syndication API fails or returns no videos:

1. Fetch bearer token from Twitter's main.js
2. Extract guest token from HTML page cookies
3. Dynamically extract GraphQL Query ID from main.js
4. Query TweetResultByRestId GraphQL endpoint
5. Parse JSON response for video variants (selects highest bitrate)
6. Handle two video types:
   - Simple: Single MP4 file
   - Segmented: MP4 container + multiple M4S chunks (assembled in memory)
7. Detect reposted videos via `source_status_id_str` and recursively download original
8. Optional: Convert MP4 to GIF for animated tweets
9. Optional: Download associated images

## Testing

Tests are located in `tests/` and use `pytest`. Test URLs are defined in `tests/test_data.toml`.

```bash
# Run all tests
uv run pytest tests/

# Run specific test
uv run pytest tests/test_download_video_for_sc.py::test_download_videos
```

**Test cleanup**: `teardown_function()` automatically removes `tests/output/` after each test.

## Version Management

Version is stored in `pyproject.toml` and updated via:

```bash
just update-version 0.2.13
# Or manually:
uv run python ci/update_pyproject_version.py 0.2.13
```

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

- Trailing whitespace removal
- End-of-file fixer
- Line ending normalization (LF)
- TOML/YAML validation
- Ruff linting and formatting
- Auto-generate `requirements.txt` and `requirements-dev.txt` from `pyproject.toml`

## Common Development Patterns

### Adding support for new video formats

1. **For Syndication API** (recommended):
   - Update `extract_media_from_syndication()` to handle new JSON structure
   - Add parsing logic for new media types
   - Add test case to `tests/test_data.toml`

2. **For GraphQL API** (fallback):
   - Update regex patterns in `extract_mp4s()` if needed
   - Add test case to `tests/test_data.toml`

3. Run tests to verify: `uv run pytest tests/`

### Handling API changes

**Syndication API changes:**

1. Update API endpoint URLs in `get_tweet_details_syndication()`
2. Adjust JSON parsing in `extract_media_from_syndication()`
3. Test with various tweet types

**GraphQL API changes:**

1. The Query ID is extracted dynamically from main.js (no manual update needed)
2. If `RequestDetails.json` needs changes, edit features/variables
3. The auto-retry mechanism will update it if Twitter rejects the request
4. Commit updated `RequestDetails.json` if changes are successful

### Adding configuration options

1. Add to `src/twitter_video_dl/settings.json`
2. Load in module using `json.load(open("./src/twitter_video_dl/settings.json"))`
3. Apply throughout codebase

## Known Limitations

- **Syndication API**: Some very old tweets or deleted tweets may not be accessible
- **GraphQL API Fallback**: Large segmented videos load entirely in memory (potential OOM for huge files)
- Browser extension only tested on Chrome/Brave
- iOS Shortcuts only tested on iPhone/iPad (not Mac)
- Requires FFmpeg for GIF conversion (not needed for iOS Shortcuts with a-Shell)
