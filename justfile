# Display default recipe list
default:
    @just --list

# Ruff related commands (corresponding to taskipy tasks)
ruffcheck:
    uv run ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci

rufffix:
    uv run ruff check twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci --fix

# Ruff format
format:
    uv run ruff format twitter-video-dl-for-sc.py twitter-video-dl.py src tests ci

# Run tests
test:
    uv run pytest tests/

# Development related commands
install:
    uv sync --extra dev

install-prod:
    uv sync

update:
    uv lock --upgrade && uv sync --extra dev

# Check for outdated packages
show-outdated:
    @echo "📦 Checking for outdated packages..."
    uv pip list --outdated

# Run pre-commit hooks
pre-commit:
    uv run pre-commit run --all-files

# Cleanup
clean:
    @echo "🧹 Cleaning up generated files..."
    rm -rf .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    @echo "✅ Cleanup completed"

# Deep cleanup (including virtual environment)
clean-all: clean
    @echo "🧹 Deep cleaning (including virtual environment)..."
    rm -rf .venv
    @echo "✅ Deep cleanup completed"

# Setup development environment
setup: install
    @echo "🚀 Setting up development environment..."
    uv run pre-commit install
    @if [ -f ".git/hooks/pre-commit" ]; then \
        echo "✅ Pre-commit hooks installed"; \
    else \
        echo "⚠️ Pre-commit hooks not installed"; \
    fi
    @echo "🎉 Development environment setup completed!"

# Update version (using ci script)
update-version version:
    @echo "📝 Updating version to {{version}}..."
    uv run python ci/update_pyproject_version.py {{version}}
    @echo "✅ Version updated to {{version}}"

# Prepare release
prepare-release version:
    @echo "🚀 Preparing release {{version}}..."
    just update-version {{version}}
    just ruffcheck
    just test
    @echo "🏷️ Create a git tag: git tag v{{version}}"
    @echo "✅ Release preparation completed!"

# Show debug information
debug-info:
    @echo "🔍 Debug Information"
    @echo "===================="
    @echo ""
    @echo "📦 Environment:"
    @echo "  Python: $(uv run python --version)"
    @echo "  uv: $(uv --version)"
    @echo "  Ruff: $(uv run ruff --version)"
    @echo "  Current directory: $(pwd)"
    @echo ""
    @echo "📋 Installed packages:"
    @uv pip list
    @echo ""
    @echo "📁 Project structure:"
    @echo "  Source: src/twitter_video_dl/"
    @echo "  Tests: tests/"
    @echo "  Scripts: ci/"

# Help
help:
    @echo "Available commands:"
    @echo ""
    @echo "🔍 Code Quality:"
    @echo "  ruffcheck            - Check code with ruff"
    @echo "  rufffix              - Fix code issues with ruff"
    @echo "  format               - Format code with ruff"
    @echo ""
    @echo "🧪 Testing:"
    @echo "  test                 - Run tests"
    @echo ""
    @echo "📦 Environment:"
    @echo "  install              - Install all dependencies"
    @echo "  install-prod         - Install production dependencies only"
    @echo "  update               - Update dependencies"
    @echo "  show-outdated        - Show outdated packages"
    @echo "  setup                - Setup development environment"
    @echo "  clean                - Clean up generated files"
    @echo "  clean-all            - Deep clean (including virtual environment)"
    @echo ""
    @echo "🚀 Development:"
    @echo "  pre-commit           - Run pre-commit hooks"
    @echo "  debug-info           - Show debug information"
    @echo ""
    @echo "🏗️ Release:"
    @echo "  update-version       - Update version (requires version)"
    @echo "  prepare-release      - Prepare for release (requires version)"
    @echo ""
    @echo "💡 Examples:"
    @echo "  just setup                    # Set up development environment"
    @echo "  just ruffcheck                # Check code"
    @echo "  just rufffix                  # Fix code issues"
    @echo "  just test                     # Run tests"
    @echo "  just prepare-release 0.2.12   # Prepare version 0.2.12 for release"
