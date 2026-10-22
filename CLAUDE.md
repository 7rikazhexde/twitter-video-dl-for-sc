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

2. **Fallback**: the tweet's own page
   - Used when Syndication API fails or returns no videos
   - No bearer/guest token or extra API call needed - X server-renders the
     `TweetResultByRestId` GraphQL result directly into the tweet page as a
     Relay record, so the fallback just parses that out of the HTML
   - Uses curl-cffi with Chrome 110 browser impersonation to avoid TLS fingerprint blocking

   > **Note**: an older fallback (`get_tokens()`/`get_tweet_details()`/
   > `create_video_urls()`) scraped a bearer token out of a `main.js` file
   > referenced by a blank "tweet not found" placeholder page. X's frontend
   > no longer serves that placeholder-and-redirect flow or that `main.js`
   > URL pattern at all, so that code path is defunct and unused by
   > `download_video_for_sc()`. It's still used by the legacy
   > `download_video()`/`twitter-video-dl.py` entry point, which is
   > correspondingly untested and not expected to work currently.

### Key Functions in `twitter_video_dl.py`

**Syndication API (Primary Method):**

- `get_tweet_details_syndication(tweet_url)`: Fetches tweet data using Syndication API (no auth required)
- `extract_media_from_syndication(syndication_data)`: Extracts video/image URLs from Syndication API response
  - Supports regular videos from `mediaDetails`
  - Supports card-type videos from `card.binding_values.unified_card` (promoted/ad tweets)

**Fallback Method (embedded tweet page data):**

- `get_tweet_result_from_page(tweet_url)`: Fetches the tweet page and extracts the embedded `TweetResultByRestId` Relay result (no tokens needed)
- `extract_media_from_tweet_result(result)`: Extracts video/image URLs from that result
  - Supports regular videos from `media_entities2`
  - Supports card-type videos from `card.legacy.binding_values` (promoted/ad tweets)

**Common Functions:**

- `download_video_for_sc(tweet_url, output_file, output_folder_path)`: Main entry point for shortcuts (tries Syndication API first, falls back to GraphQL)
- `download_videos(video_urls, ...)`: Downloads videos with optional GIF conversion via FFmpeg
- `get_img(urls, ...)`: Downloads images if `image.save_option` is enabled

### Auto-Retry Mechanism (legacy GraphQL fallback)

The unused legacy `get_tweet_details()` function includes smart retry logic (max 10 attempts) that:

- Detects missing Twitter API "features" or "variables" from 400 errors
- Automatically adds required parameters to the request
- Updates `RequestDetails.json` on successful retry
- This handled Twitter's frequent API parameter changes, back when that endpoint was reachable this way

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

**Important**: When running `just test`, ensure `image.save_option` is `true` for full test coverage (debug_option can be false for normal testing).

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

**Fallback Flow (embedded tweet page data):**

Used when Syndication API fails or returns no videos:

1. Normalize URL (twitter.com → x.com) and validate its host
2. Fetch the tweet page with curl-cffi (Chrome 110 impersonation)
3. Find the page's embedded `TweetResultByRestId` Relay record and parse its
   JSON-escaped `value` string
4. Extract video variants from `media_entities2` (or `card.legacy.binding_values`
   for promoted/ad tweets), selecting the highest bitrate
5. Optional: Convert MP4 to GIF for animated tweets
6. Optional: Download associated images

## Testing

Tests are located in `tests/` and use `pytest`. Test URLs are defined in `tests/test_data.toml`.

### Test Files

1. **`test_syndication_api.py`** - Syndication API unit tests (5 tests)
2. **`test_graphql_api.py`** - Fallback method unit tests (embedded tweet page data, 5 tests)
3. **`test_comprehensive_comparison.py`** - Full test suite using test_data.toml (34 test cases total)
   - Tests Syndication API with all 17 test_data.toml cases
   - Tests the fallback method with all 17 test_data.toml cases

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_syndication_api.py
uv run pytest tests/test_graphql_api.py
uv run pytest tests/test_comprehensive_comparison.py
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

2. **For the fallback method**:
   - Update `extract_media_from_tweet_result()` to handle new JSON structure
   - Add test case to `tests/test_data.toml`

3. Run tests to verify: `uv run pytest tests/`

### Handling API changes

**Syndication API changes:**

1. Update API endpoint URLs in `get_tweet_details_syndication()`
2. Adjust JSON parsing in `extract_media_from_syndication()`
3. Test with various tweet types

**GraphQL API changes:**

1. Query ID is dynamically extracted from main.js at runtime
2. Automatic adaptation to X (Twitter) Query ID changes without manual updates
3. If Query ID extraction fails, check and update the regex pattern in `get_tokens()` function
4. If `RequestDetails.json` needs changes, edit features/variables
5. The auto-retry mechanism will update it if Twitter rejects the request
6. Commit updated `RequestDetails.json` if changes are successful

### Adding configuration options

1. Add to `src/twitter_video_dl/settings.json`
2. Load in module using `json.load(open("./src/twitter_video_dl/settings.json"))`
3. Apply throughout codebase

## Known Limitations

- **Syndication API**: Some very old tweets or deleted tweets may not be accessible
- **Fallback method (embedded tweet page data)**:
  - Requires curl-cffi for TLS fingerprint handling (falls back to standard requests if unavailable)
  - Depends on X continuing to embed the `TweetResultByRestId` Relay result in the tweet page; if X changes that rendering approach, `get_tweet_result_from_page()`'s extraction pattern will need updating
  - The older `get_tokens()`/`get_tweet_details()`/`create_video_urls()` path (scraping a bearer token from `main.js`) is defunct against X's current frontend and unused by `download_video_for_sc()` - see the API Approach section
- Browser extension only tested on Chrome/Brave
- iOS Shortcuts only tested on iPhone/iPad (not Mac)
- Requires FFmpeg for GIF conversion (not needed for iOS Shortcuts with a-Shell)
