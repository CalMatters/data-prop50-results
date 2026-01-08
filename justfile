generate-precincts-file:
    uv run 01_geography.py

merge-precinct-results:
    uv run 03_precincts_merge.py
