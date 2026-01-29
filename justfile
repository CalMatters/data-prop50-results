generate-precincts-file:
    uv run 01_geography.py

generate-results-file:
    uv run 02_results.py

generate-cvap-file:
    uv run 02_census.py
    uv run 02b_census.py

merge-precinct-results:
    uv run 03_precincts_merge.py

interpolate-cvap:
    uv run 04_interpolation.py

generate-all-data:
    just generate-precincts-file
    just generate-results-file
    just generate-cvap-file
    just merge-precinct-results
    just interpolate-cvap

generate-demographics-pmtiles:
    npx mapshaper outputs/precinct_results_plus_demographics.geojson -proj wgs84 init=EPSG:3310 -o format=geojson ndjson outputs/precinct_results_plus_demographics_nd.json
    tippecanoe -f -l precincts -o outputs/precinct_results_plus_demographics.pmtiles --maximum-zoom=14 --minimum-zoom=4 --read-parallel outputs/precinct_results_plus_demographics_nd.json
    cp outputs/precinct_results_plus_demographics.pmtiles vis/static/precinct_results_plus_demographics.pmtiles