# Fixer CLI

A comprehensive CLI tool for fixing issues and maintaining code quality. Built with Typer for a modern, user-friendly command-line experience.

## Features

- 🔧 **Fix Issues**: Automated git workflow for fixing issues with proper logging
- 🔍 **Diagnose Problems**: Run diagnostics to identify code issues
- 🧹 **Refactor Code**: Automated code formatting and linting
- 📋 **Comprehensive Logging**: Track all fixes in `FIX_LOG.md`

## Installation

### From Source

```bash
# Clone or download the fixer.py file
# Then install in development mode
pip install -e .
```

### Direct Installation

```bash
# Install required dependencies
pip install typer[all] black isort flake8 gitpython

# Make fixer.py executable
chmod +x fixer.py

# Run directly
python fixer.py --help
```

## Commands

### `fix` - Fix a Single Issue

Creates a new git branch, waits for manual fixes, commits changes, and logs results.

```bash
fixer fix <tag> <description> [--notes "optional notes"]
```

**Example:**
```bash
fixer fix bug "fix authentication error in login"
fixer fix feature "add user profile page" --notes "includes avatar upload"
```

**What it does:**
1. Creates branch: `fix/{tag}-{description}`
2. Waits for you to apply and stage fixes
3. Prompts for test results (PASS/FAIL)
4. Commits and pushes changes
5. Logs results to `FIX_LOG.md`

### `diagnose` - Run Diagnostics

Executes the diagnostic script to identify issues.

```bash
fixer diagnose
```

**Example:**
```bash
fixer diagnose
# Runs diagnostic_script.py and shows results
```

### `atest` - Alias for Diagnose

Same as `diagnose` command.

```bash
fixer atest
```

### `refa` - Refactor Codebase

Runs code formatting and linting tools.

```bash
fixer refa
```

**What it does:**
- Runs `black .` for code formatting
- Runs `isort .` for import organization  
- Runs `flake8` for linting
- **Does NOT auto-commit** (safe for preview)

## Logging

All fix operations are logged to `FIX_LOG.md` with the following information:

- ✅ **Status**: FIXED or FAILED
- 🕒 **Timestamp**: When the fix was applied
- 🏷️ **Tag**: Issue tag (bug, feature, etc.)
- 📄 **Files Modified**: List of changed files
- 🧩 **Summary**: Description of the fix
- 🔍 **Test Result**: PASS or FAIL
- 💬 **Notes**: Optional additional notes

## Requirements

- Python 3.8+
- Git repository
- Required tools for `refa` command:
  - `black` (code formatting)
  - `isort` (import organization)
  - `flake8` (linting)

## Installation of Required Tools

```bash
# Install all required tools
pip install black isort flake8

# Or install individually
pip install black
pip install isort
pip install flake8
```

## Example Workflow

```bash
# 1. Run diagnostics to find issues
fixer diagnose

# 2. Fix an issue
fixer fix bug "fix null pointer exception in user service"

# 3. Apply your fix manually, then stage changes
git add .

# 4. Continue with fixer (it will prompt for test results)

# 5. Refactor code (optional)
fixer refa

# 6. Review and commit refactoring changes manually
git diff
git add .
git commit -m "refactor: apply code formatting and linting"
```

## Configuration

The tool uses these default files:
- `FIX_LOG.md` - Log file for all fixes
- `diagnostic_script.py` - Diagnostic script to run

## Error Handling

- Validates git repository before operations
- Checks for required tools before running refa
- Provides clear error messages and suggestions
- Graceful handling of git operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the `FIX_LOG.md` for recent fixes
- Run `fixer diagnose` to identify problems
- Review the help: `fixer --help` 