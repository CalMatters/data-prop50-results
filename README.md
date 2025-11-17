# data-prop50-results
An analysis of 2025 election results for prop 50

## Quick Start

This project uses [Marimo](https://marimo.io/) (an interactive Python notebook) and [uv](https://github.com/astral-sh/uv) (a fast Python package manager).

### Setup (First Time Only)

1. **Install uv** (if you don't have it):
   ```bash
   brew install uv
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

### Running the Notebook

Start the Marimo notebook:
```bash
uv run marimo edit 00_demo.py
```

This will:
- Open the notebook in your browser
- Allow you to edit and run code interactively
- Auto-save changes as you work

### Development Workflow

1. Open the notebook: `uv run marimo edit 00_demo.py`
2. Make changes in the browser interface
3. Changes are automatically saved to `00_demo.py`
4. Share your changes via git (the `.py` file is the notebook)

**Note**: Marimo notebooks are just Python files - you can edit them in any editor, but the browser interface makes it easier to run and visualize results.
