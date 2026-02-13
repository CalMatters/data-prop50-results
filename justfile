generate-precincts-file:
    uv run 01_geography.py

generate-results-file:
    uv run 02a_results_2025.py
    uv run 02b_results_2024.py

generate-cvap-file:
    uv run 00_census.py

merge-precinct-results:
    uv run 03_precincts_merge.py

interpolate-cvap:
    uv run 04_interpolation.py

generate-all-data:
    just generate-precincts-file
    just generate-results-file
    just merge-precinct-results
    just generate-cvap-file
    just interpolate-cvap

generate-demographics-pmtiles:
    npx mapshaper outputs/precinct_results_plus_demographics_blocks.geojson -proj wgs84 init=EPSG:3310 -o format=geojson ndjson outputs/precinct_results_plus_demographics_blocks_nd.json
    tippecanoe -f -l precincts -o outputs/precinct_results_plus_demographics_blocks.pmtiles --maximum-zoom=14 --minimum-zoom=4 --read-parallel outputs/precinct_results_plus_demographics_blocks_nd.json
    cp outputs/precinct_results_plus_demographics_blocks.pmtiles vis/static/precinct_results_plus_demographics_blocks.pmtiles
