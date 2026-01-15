generate-precincts-file:
    uv run 01_geography.py

generate-results-file:
    uv run 02_results.py

generate-cvap-file:
    uv run 02_census.py

generate-data:
    just generate-precincts-file
    just generate-results-file
    just generate-cvap-file

merge-precinct-results:
    uv run 03_precincts_merge.py
