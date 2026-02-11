# data-prop50-results
An analysis of 2025 election results for Prop. 50 using precinct-level data from counties. We are keeping track of what each county publishes and where [in this Google spreadsheet](https://docs.google.com/spreadsheets/d/1TRuXAbeOSlQe1VakQSi42ijHQiILivoAg4rlw7vG0fY/edit?gid=1241525250#gid=1241525250). 

## Data sources
* Precinct results and geographic files - [from each county](https://docs.google.com/spreadsheets/d/1TRuXAbeOSlQe1VakQSi42ijHQiILivoAg4rlw7vG0fY/edit?gid=0#gid=0)
* Current congressional district geographic files - [We Draw the Lines, the independent redistricting commission](https://wedrawthelines.ca.gov)
* Census Voting Age Population (CVAP) - [Census](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html)

## Quick Start

This project uses [Marimo](https://marimo.io/) (an interactive Python notebook) and [uv](https://github.com/astral-sh/uv) (a fast Python package manager). This project uses [just](https://github.com/casey/just) to quickly run project scripts.

### Setup (First Time Only)

1. **Install uv and just** (if not already installed):
   ```bash
   brew install uv
   brew install just
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

### Generate intermediary data files

1. **Generate statewide precincts data file**:
   ```bash
   just generate-precincts-file
   ```

2. **Merge precinct geography with results**:
   ```bash
   just merge-precinct-results
   ```

### Data Processing Workflow

The notebooks follow a sequential pipeline:

1. **`00_census.py`** - Census ETL: county bounds, CVAP by tract, CVAP by block
   - Output: `outputs/county_bounds.geojson`, `outputs/cvap_tracts.gpkg`, `outputs/cvap_blocks.gpkg`
   - Run with: `just generate-cvap-file`

2. **`01_geography.py`** - Processes precinct geographic files from all counties
   - Output: `outputs/precincts.gpkg`
   - Run with: `just generate-precincts-file`

3. **`02a_results_2025.py`** and **`02b_results_2024.py`** - Clean and standardize precinct-level election results
   - Output: `02a` → `outputs/results.csv`; `02b` → `outputs/precinct_results_2024.gpkg` (and county-level outputs in `outputs/counties/`)
   - Run with: `uv run marimo edit 02a_results_2025.py` or `uv run marimo edit 02b_results_2024.py` (interactive), or `just generate-results-file` to run both

4. **`03_precincts_merge.py`** - Merges geography and results data
   - Input: `outputs/precincts.gpkg` and `outputs/results.csv`
   - Output: `outputs/precinct_results.gpkg`
   - Run with: `just merge-precinct-results`

### Notebooks

We use [Marimo](https://marimo.io) notebooks to do analysis and to clean data. If you want to use a particular notebook, let's say "`01_geography.py`" you should use the following command:

```bash
uv run marimo edit 01_geography.py
```

This will:
- Open the notebook in your browser
- Allow you to edit and run code interactively
- Auto-save changes as you work

**Note**: Marimo notebooks are just Python files - you can edit them in any editor, but the browser interface makes it easier to run and visualize results.

Notebooks include:

* `00_census.py` - Census ETL: county bounds, CVAP by tract, CVAP by block
* `01_geography.py` - Precinct geographic data cleaning
* `02a_results_2025.py` - 2025 precinct result data cleaning
* `02b_results_2024.py` - 2024 precinct result data cleaning
* `03_precincts_merge.py` - Merge precinct geography with results data

All notebooks read data from `inputs/` and write data to `outputs/`. See the "Data Processing Workflow" section above for details on how they connect.

#### Development Workflow

1. Open the notebook: `uv run marimo edit FILENAME`
2. Make changes in the browser interface
3. Changes are automatically saved to `FILENAME.py`
4. Share your changes via git (the `.py` file is the notebook)

#### `01_geography.py` - Precinct geographic data cleaning

Reproject the voting precincts from each county into NAD83/California Albers and normalize the properties for each feature (precinct) so that it has the following attributes:
 * `county` - The county containing the precinct
 * `precinct_id` - The precinct ID from the county
 * `precinct_name` - The human-readable name included by the county, otherwise `None`

#### `00_census.py` - Census ETL

Produces three GIS outputs: California county boundaries (`outputs/county_bounds.geojson`), [CVAP](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) by census tract (`outputs/cvap_tracts.gpkg`), and CVAP by block (`outputs/cvap_blocks.gpkg`). All use NAD83/California Albers (EPSG:3310). Run with `just generate-cvap-file`.

#### `02a_results_2025.py` and `02b_results_2024.py` - Precinct result data cleaning

Make sure that the precinct-level results data has the following columns for consistency:
* `county` - The county containing the precinct
* `precinct_id` - Unique ID for the precinct
* `yes_votes` - the number of votes for "Yes" on Prop. 50 in the precinct
* `no_votes` - the number of votes for "No" on Prop. 50 in the precinct
* `turnout` - the percent of the voters who cast a ballot in the precinct, included if included by the county; range is 0 to 100

#### `03_precincts_merge.py` - Merge precinct geography with results

Merges the standardized precinct geography file (`outputs/precincts.gpkg`) with the cleaned results data (`outputs/results.csv`) to create a combined GeoPackage file. The merge is performed on `county` and `precinct_id` columns. The notebook includes:

* Duplicate detection and reporting
* Audit functions to identify missing entries
* Export of merged data to `outputs/precinct_results.gpkg`

## Output Files

The notebooks generate the following output files in the `outputs/` directory:

* `precincts.gpkg` - Combined precinct geography from all counties (from `01_geography.py`)
* `results.csv` - Standardized precinct-level 2025 election results (from `02a_results_2025.py`)
* `precinct_results.gpkg` - Merged geography and results data (from `03_precincts_merge.py`)
* `precinct_results_2024.gpkg` - 2024 statewide merged results (from `02b_results_2024.py`); county-level outputs in `outputs/counties/`

**Note**: Most output files are gitignored (see `.gitignore`).
