# Latino voters shifted towards Prop. 50. Here’s how we analyzed it. 

An analysis of 2025 election results for Prop. 50 using precinct-level data. This repository contains the **code and processing pipeline** used to build precinct-level datasets. For the full narrative methodology and findings framing, see [Show Your Work](https://calmatters.org/show-your-work/2026/05/latino-voters-shifted-towards-prop-50-heres-how-we-analyzed-it). 

Published story: [Latinos in California are mad at Trump. Their votes for Democrats’ gerrymandering show it](https://calmatters.org/politics/2026/05/california-latino-voters-prop50-analysis)

## Data sources

- Precinct results, geographic, and voter demographics files from the [Statewide Database](https://statewidedatabase.org/).
- [Census Voting Age Population](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) (CVAP) disaggregated by the [Redistricting Voting Hub](https://redistrictingdatahub.org/dataset/california-cvap-data-disaggregated-to-the-2020-block-level-2024/).

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

## Quick start

This project uses [Marimo](https://marimo.io/) (an interactive Python notebook) and [uv](https://github.com/astral-sh/uv) (a fast Python package manager). This project uses [just](https://github.com/casey/just) to quickly run project scripts.

### Setup (first time only)

1. **Install uv and just** (if not already installed):
  ```bash
   brew install uv
   brew install just
  ```
2. **Install dependencies**:
  ```bash
   uv sync
  ```

### Run the pipeline

After required inputs are in place under `./inputs/` (see above), run stages in order or use the combined recipe:


| Step                 | Command                          | Purpose                                                            |
| -------------------- | -------------------------------- | ------------------------------------------------------------------ |
| CVAP / county bounds | `just generate-cvap-file`        | `00_census.py`                                                     |
| Precinct geometries  | `just generate-precincts-file`   | `01_geography.py`                                                  |
| Standardized results | `just generate-results-file`     | `02a_results_2025.py`, `02b_results_2024.py`                       |
| Interpolation        | `just interpolate-cvap`          | `03_interpolation.py`                                              |
| Analysis exports     | `just generate-analysis-exports` | `04_analysis.py`                                                   |
| Full sequence        | `just generate-all-data`         | All of the above (also updates `vis/static/county_precincts.json`) |


Individual notebooks can be opened interactively with `uv run marimo edit <notebook>.py`.

### Limitations and practical notes

- **Large inputs**: Census zips and statewide database files are large; allow plenty of disk space under `./inputs/` and `./outputs/`.
- **Network fallbacks**: If automatic downloads fail, place the files at the paths listed under Network-dependent data.
- **Runtime**: Full runs are heavy geospatial work; expect long runtimes on a laptop for the whole pipeline.
- **Redactions**: Some precincts have suppressed counts in source data; the pipeline preserves blanks where administrative redactions apply.
- **Interpolation**: Cross-year precinct boundary and areal-interpolation steps introduce assumptions; see our [Show Your Work](https://calmatters.org/show-your-work/2026/05/latino-voters-shifted-towards-prop-50-heres-how-we-analyzed-it).

## Data processing workflow

The notebooks follow a sequential pipeline:

1. `00_census.py` — Census ETL: county bounds, CVAP by tract, CVAP by block
  - Output: `outputs/county_bounds.geojson`, `outputs/cvap_tracts.gpkg`, `outputs/cvap_blocks.gpkg`  
  - Run with: `just generate-cvap-file`
2. `01_geography.py` — Processes precinct geographic files from all counties
  - Output: `outputs/precincts.gpkg`  
  - Run with: `just generate-precincts-file`
3. `02a_results_2025.py` and `02b_results_2024.py` — Clean and standardize precinct-level election results
  - Output: `02a` → `outputs/precinct_results.gpkg`; `02b` → `outputs/precinct_results_2024.gpkg`  
  - Run with: `uv run marimo edit 02a_results_2025.py` or `uv run marimo edit 02b_results_2024.py` (interactive), or `just generate-results-file` to run both
4. `03_interpolation.py` — Interpolates Census CVAP demographics to precincts and 2024 vote data to 2025 precincts
  - Input: `outputs/precinct_results.gpkg`, `outputs/precinct_results_2024.gpkg`, `outputs/cvap_tracts.gpkg`, `outputs/cvap_blocks.gpkg`  
  - Output: `outputs/precincts_results_cvap_tracts.gpkg`, `outputs/precincts_results_cvap_blocks.gpkg`, `outputs/precincts_2024_results_cvap_blocks.gpkg`
5. `04_analysis.py` — Analysis and exports from interpolated datasets
  - Input: merged/interpolated GeoPackages from `03_interpolation.py`  
  - Output: `outputs/precinct_results_plus_demographics_*.gpkg`, `outputs/partner_export.csv`, GeoJSON used for optional map tiles (see notebook)
6. `05_fact_check.py` — Fact-check workbook for story and methodology claims
  - Input: `outputs/precincts_results_cvap_blocks.gpkg`, `outputs/precincts_2024_results_cvap_blocks.gpkg`, `inputs/statewide_db/state_g24_sr_blk_map.csv`
  - Output: in-notebook verification text/metrics used to validate published statements (no data export)

### Notebooks

If you want to use a particular notebook (for example `01_geography.py`):

```bash
uv run marimo edit 01_geography.py
```

This opens the notebook in your browser, runs code interactively, and auto-saves changes to the `.py` file.

**Note**: Marimo notebooks are plain Python files—you can edit them in any editor, but the browser UI helps run and visualize results.

#### Development workflow

1. Open the notebook: `uv run marimo edit FILENAME`
2. Make changes in the browser interface
3. Changes are automatically saved to `FILENAME.py`
4. Share your changes via git (the `.py` file is the notebook)

#### `01_geography.py` — Precinct geographic data cleaning

Reproject the voting precincts from each county into NAD83/California Albers and normalize the properties for each feature (precinct) so that it has the following attributes:

- `county` — The county containing the precinct  
- `precinct_id` — The precinct ID from the county  
- `precinct_name` — The human-readable name included by the county, otherwise `None`

#### `00_census.py` — Census ETL

Produces three GIS outputs in NAD83/California Albers (EPSG:3310): California county boundaries (`outputs/county_bounds.geojson`), [CVAP](https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html) by census tract (`outputs/cvap_tracts.gpkg`), and CVAP by block (`outputs/cvap_blocks.gpkg`). Run with `just generate-cvap-file`.

#### `02a_results_2025.py` and `02b_results_2024.py` — Precinct-level results standardization

Standardizes statewide election results into a consistent schema for downstream geospatial analysis.

#### `03_interpolation.py` — Merge and interpolate CVAP to precinct geography

Builds precinct-level analysis layers by combining election results with CVAP inputs and running tract/block interpolation workflows. The notebook includes:

- Geometry/data validation and reprojection checks  
- Merge audits and county-level mismatch diagnostics  
- Export of precinct-level CVAP-enriched outputs (including `outputs/precincts_2024_results_cvap_blocks.gpkg`)

#### `04_analysis.py` — Demographics and precinct-level results analysis

Runs exploratory and comparative analysis on the merged precinct datasets, including statewide and county-level majority-group summaries, vote-shift calculations, and dataset-specific breakouts.

#### `05_fact_check.py` — Fact-check checks for editorial claims

Recomputes core published facts values from the merged precinct datasets. This notebook is for validation of published facts and presents dynamic claim markdown text reproducing the published. If you are looking to trace the data and analysis for our published report, you should start in this notebook.

## Output files

Generated files land in `outputs/` (gitignored except as noted). Typical artifacts:


| File                                                  | Produced by           | Description                                                                       |
| ----------------------------------------------------- | --------------------- | --------------------------------------------------------------------------------- |
| `county_bounds.geojson`                               | `00_census.py`        | California counties (EPSG:3310)                                                   |
| `cvap_tracts.gpkg`, `cvap_blocks.gpkg`                | `00_census.py`        | CVAP layers by tract / block                                                      |
| `precincts.gpkg`                                      | `01_geography.py`     | Combined precinct polygons (`county`, `precinct_id`, `precinct_name`, `geometry`) |
| `precinct_results.gpkg`                               | `02a_results_2025.py` | 2025 Prop. 50 results joined to geometry                                          |
| `precinct_results_2024.gpkg`                          | `02b_results_2024.py` | 2024 presidential-style fields on 2024 precincts                                  |
| `precincts_results_cvap_*.gpkg`                       | `03_interpolation.py` | Interpolated CVAP + votes                                                         |
| `precinct_results_plus_demographics_blocks.gpkg`      | `04_analysis.py`      | Analysis-layer export (blocks / Prop 50)                                          |
| `precinct_results_plus_demographics_blocks_2024.gpkg` | `04_analysis.py`      | Analysis-layer export (blocks / 2024 presidential comparison)                     |
| `partner_export.csv`                                  | `04_analysis.py`      | Tabular partner export (see data dictionary below)                                |
| `precinct_results_plus_demographics_blocks.geojson`   | `04_analysis.py`      | Optional map/interactive intermediate                                             |


**Note**: Most output files are gitignored (see `.gitignore`).

## Data dictionary (primary exports)

### `partner_export.csv` (from `04_analysis.py`)

Percent columns in the CSV are stored as **fractions** between 0 and 1 (for example, 0.5 for 50%), suitable for spreadsheets that format as percent.


| Column                         | Description                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `county`                       | County name                                                                               |
| `precinct_id`                  | Precinct identifier (joined key)                                                          |
| `total_votes_25`               | Total votes counted for Prop. 50 in the precinct                                          |
| `yes_votes`, `no_votes`        | Vote counts for Yes / No on Prop. 50                                                      |
| `yes_pct`, `no_pct`            | Yes / No shares of two-party vote (fractions 0–1)                                         |
| `registered_voters`            | Registered voters where available from source data                                        |
| `turnout`                      | Turnout measure used in analysis (fraction 0–1)                                           |
| `total_votes_24`               | Total votes in 2024 presidential contest (interpolated to 2025 precinct where applicable) |
| `dem_votes_24`, `rep_votes_24` | Democratic / Republican presidential votes (interpolated baseline)                        |
| `dem_pct_24`, `rep_pct_24`     | Democratic / Republican presidential vote shares (fractions 0–1)                          |
| `vote_shift_net`               | Net swing metric between elections                                                        |
| `majority_racial_group`        | CVAP-based majority racial/ethnic group label for the precinct                            |
| `plurality_racial_group`       | Plurality group where coded                                                               |
| `largest_racial_group_pct`     | Share for the largest single CVAP group (fraction 0–1)                                    |


### Key GeoPackage layers

- `**precincts.gpkg`** — Attributes: `county`, `precinct_id`, `precinct_name`; geometry in EPSG:3310.  
- `**precinct_results.gpkg` / `precinct_results_2024.gpkg`** — Standardized vote and registration fields for 2025 and 2024 respectively; see notebook export lists in `02a_results_2025.py` and `02b_results_2024.py` for exact column names per vintage.  
- `**precinct_results_plus_demographics_*.gpkg`** — Enriched analysis layers from `04_analysis.py` combining votes with interpolated CVAP demographics; column sets follow the analysis dataset configuration inside `04_analysis.py`.

For interpretation of demographic groupings, net shift, and limitations, rely on our [Show Your Work](https://calmatters.org/show-your-work/2026/05/latino-voters-shifted-towards-prop-50-heres-how-we-analyzed-it)

## Examples of Use

- [Latinos in California are mad at Trump. Their votes for Democrats’ gerrymandering show it](https://calmatters.org/politics/2026/05/california-latino-voters-prop50-analysis/)
- [Latino voters shifted towards Democrats on Prop. 50. Here’s how we analyzed it.](https://calmatters.org/show-your-work/2026/05/latino-voters-shifted-towards-prop-50-heres-how-we-analyzed-it/)

## Data use

While the contents of this repo are shared under an Apache 2.0 license, CalMatters/The Markup would appreciate any credit or attribution you're willing to give. We're also interested to learn how you used it, so feel free to [send us a message](john@calmatters.org) or open an issue if you do. If you have any questions, feel free to [contact us](john@calmatters.org) as well.

CalMatters is a nonpartisan, nonprofit journalism venture committed to explaining how California’s state Capitol works and why it matters.

## Contact and issues

For bugs, unclear documentation, or questions about the pipeline, use [GitHub Issues](https://github.com/CalMatters/data-prop50-results/issues) or send us an [email](data@calmatters.org).

## Note on AI-assisted work

> We used AI coding tools to assist with the analysis. All results were manually reviewed by a member of our team.

## License

Code in this repository is licensed under the Apache License, Version 2.0; see [LICENSE](LICENSE). Dependency licenses are managed by PyPI packages; see [NOTICE](NOTICE).
