generate-precincts-file:
    uv run 01_geography.py

generate-results-file:
    uv run 02_results.py

generate-precincts-and-results:
    just generate-precincts-file
    just generate-results-file

merge-precinct-results:
    uv run 03_precincts_merge.py
