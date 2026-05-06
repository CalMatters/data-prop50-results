# data-prop50-results
An analysis of 2025 election results for Prop. 50 using precinct-level data from counties. We are keeping track of what each county publishes and where [in this Google spreadsheet](https://docs.google.com/spreadsheets/d/1TRuXAbeOSlQe1VakQSi42ijHQiILivoAg4rlw7vG0fY/edit?gid=1241525250#gid=1241525250). 

## Data sources
* Precinct results, geographic, and voter demographics files from the [Statewide Database](https://statewidedatabase.org/).
* [Census Voting Age Population](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) (CVAP) disaggregated by the [Redistricting Voting Hub](https://redistrictingdatahub.org/dataset/california-cvap-data-disaggregated-to-the-2020-block-level-2024/).

### Filepaths

- `./inputs/census/CVAP_2020-2024_ACS_csv_files.zip`  
  - Census CVAP special tabulation zip consumed by `00_census.py` (`CVAP_ZIPPED_DATA_FP`)
  - Data used for validation and experimentation
- `./inputs/rdh/ca_cvap_2024_2020_b_csv/ca_cvap_2024_2020_b.csv`  
  - Redistricting Data Hub 2024 CVAP block-level extract consumed by `00_census.py` (`RDH_CVAP_DATA_FP`)
  - Data used for interpolating precinct demographics
- `./inputs/statewide_db/` General Election 2024 files
  - Expected core files used by `02b_results_2024.py`:
    - Election results: `state_g24_sov_data_by_g24_srprec.zip` 
    - Voter demographics: `state_g24_voters_by_g24_srprec.zip`
    - Precinct geographic boundaries: `srprec_state_g24_v01_shp.zip`
- `./inputs/statewide_db/S25/` Special Election 2025 files
  - Expected county-level 2025 election results, voter demographics, and precinct boundaries inputs used by the 2025 results workflow

### Network-dependent data

These files were excluded from version control due to file size limits. If missing, notebooks will try and fetch them over the network:

- `00_census.py`
  - Local expected file: `./inputs/census/tl_2020_06_tabblock20.zip`
  - Fallback URL: `https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_06_tabblock20.zip`
- `02b_results_2024.py`
  - Local expected file: `./inputs/statewide_db/srprec_state_g24_v01_shp.zip`
  - Fallback URL: `https://statewidedatabase.org/pub/data/G24/state/srprec_state_g24_v01_shp.zip`

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
   - Output: `02a` → `outputs/precinct_results.gpkg`; `02b` → `outputs/precinct_results_2024.gpkg`
   - Run with: `uv run marimo edit 02a_results_2025.py` or `uv run marimo edit 02b_results_2024.py` (interactive), or `just generate-results-file` to run both

4. **`03_interpolation.py`** - Interpolates Census CVAP demographics to precincts and 2024 vote data to 2025 precincts
   - Input: `outputs/precinct_results.gpkg`, `outputs/precinct_results_2024.gpkg`, `outputs/cvap_tracts.gpkg`, `outputs/cvap_blocks.gpkg`
   - Output: `outputs/precincts_results_cvap_tracts.gpkg`, `outputs/precincts_results_cvap_blocks.gpkg`, `outputs/precincts_2024_results_cvap_blocks.gpkg`

5. **`04_analysis.py`** - Analysis and exports from interpolated datasets
   - Input: merged/interpolated GeoPackages from `03_interpolation.py`
   - Output: `outputs/precinct_results_plus_demographics_*.gpkg`, `outputs/partner_export.csv`

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

Produces three GIS outputs in NAD83/California Albers (EPSG:3310): California county boundaries (`outputs/county_bounds.geojson`), [CVAP](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) by census tract (`outputs/cvap_tracts.gpkg`), and CVAP by block (`outputs/cvap_blocks.gpkg`). Run with `just generate-cvap-file`.

#### `02a_results_2025.py` and `02b_results_2024.py` - Precinct-level results standardization

Standardizes statewide election results into a consistent schema for downstream geospatial analysis. 

#### `03_interpolation.py` - Merge and interpolate CVAP to precinct geography

Builds precinct-level analysis layers by combining election results with CVAP inputs and running tract/block interpolation workflows. The notebook includes:

* Geometry/data validation and reprojection checks
* Merge audits and county-level mismatch diagnostics
* Export of precinct-level CVAP-enriched outputs (including `outputs/precincts_2024_results_cvap_blocks.gpkg`)

#### `04_analysis.py` - Demographics and precinct-level results analysis

Runs exploratory and comparative analysis on the merged precinct datasets, including statewide and county-level majority-group summaries, vote-shift calculations, and dataset-specific breakouts.



## Output Files

The notebooks generate the following output files in the `outputs/` directory:

* `precincts.gpkg` - Combined precinct geography from all counties (from `01_geography.py`)
* `results.csv` - Standardized precinct-level 2025 election results (from `02a_results_2025.py`)
* `precinct_results.gpkg` - Merged geography and results data (from `03_precincts_merge.py`)
* `precinct_results_2024.gpkg` - 2024 statewide merged results (from `02b_results_2024.py`); county-level outputs in `outputs/counties/`

**Note**: Most output files are gitignored (see `.gitignore`).
