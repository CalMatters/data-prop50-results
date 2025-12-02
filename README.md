# data-prop50-results
An analysis of 2025 election results for Prop. 50 using precinct-level data from counties. We are keeping track of what each county publishes and where [in this Google spreadsheet](https://docs.google.com/spreadsheets/d/1TRuXAbeOSlQe1VakQSi42ijHQiILivoAg4rlw7vG0fY/edit?gid=1241525250#gid=1241525250). 

## Data sources
* Precinct results and geographic files - [from each county](https://docs.google.com/spreadsheets/d/1TRuXAbeOSlQe1VakQSi42ijHQiILivoAg4rlw7vG0fY/edit?gid=0#gid=0)
* Current congressional district geographic files - [We Draw the Lines, the independent redistricting commission](https://wedrawthelines.ca.gov)
* Census Voting Age Population (CVAP) - [Census](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html)

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

### Notebooks

We use [Marimo](https://marimo.io) notebooks to do analysis and to clean data. If you want to use a particular notebook, let's say "`00_demo.py`" you should use the following command:

```bash
uv run marimo edit 00_demo.py
```

This will:
- Open the notebook in your browser
- Allow you to edit and run code interactively
- Auto-save changes as you work

**Note**: Marimo notebooks are just Python files - you can edit them in any editor, but the browser interface makes it easier to run and visualize results.

There are two notebooks:

* `00_demo.py` - Areal interpolation exploration
* `01_geography.py` - Precinct geographic data cleaning

Both read data from `inputs/` and write data to `outputs/`.

#### Development Workflow

1. Open the notebook: `uv run marimo edit FILENAME`
2. Make changes in the browser interface
3. Changes are automatically saved to `FILENAME.py`
4. Share your changes via git (the `.py` file is the notebook)

#### `00_demo.py` - Areal interpolation exploration

We used the [tobler](https://pysal.org/tobler/) library to do areal interpolation and apportion Census data to voting precincts.

#### `01_geography.py` - Precinct geographic data cleaning

Reproject the voting precincts from each county into NAD83/California Albers and normalize the properties for each feature (precinct) so that it has the following attributes:
 * `county` - The county containing the precinct
 * `precinct_id` - The precinct ID from the county
 * `precinct_name` - The human-readable name included by the county, otherwise `None`