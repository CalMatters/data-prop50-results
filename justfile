generate-precincts-file:
    uv run 01_geography.py

generate-results-file:
    uv run 02a_results_2025.py
    uv run 02b_results_2024.py

generate-cvap-file:
    uv run 00_census.py

interpolate-cvap:
    uv run 04_interpolation.py

generate-analysis-exports:
    uv run 05_analyze_demographics.py

generate-all-data:
    rm -rf outputs
    mkdir -p outputs
    just generate-precincts-file
    just generate-results-file
    just generate-cvap-file
    just interpolate-cvap
    just generate-analysis-exports
    mv outputs/county_precincts.json vis/static/

update-election-data:
    just generate-precincts-file
    just generate-results-file
    just interpolate-cvap
    just generate-analysis-exports
    mv outputs/county_precincts.json vis/static/

generate-demographics-pmtiles:
    npx mapshaper outputs/precinct_results_plus_demographics_blocks.geojson -proj wgs84 init=EPSG:3310 -o format=geojson ndjson outputs/precinct_results_plus_demographics_blocks_nd.json
    tippecanoe -f -l precincts -o outputs/precinct_results_plus_demographics_blocks.pmtiles --maximum-zoom=14 --minimum-zoom=4 --read-parallel outputs/precinct_results_plus_demographics_blocks_nd.json
    mv outputs/precinct_results_plus_demographics_blocks.pmtiles vis/static/precinct_results_plus_demographics_blocks.pmtiles
    rm outputs/precinct_results_plus_demographics_blocks.geojson
    rm outputs/precinct_results_plus_demographics_blocks_nd.json
