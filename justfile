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

generate-congressional-pmtiles:
    unzip -o inputs/wedrawthelines/OneDrive_2023-01-19-2.zip -d inputs/wedrawthelines/
    npx mapshaper inputs/wedrawthelines/CD_Final\ shapefile/CD_Final\ 2021-12-20.shp -o format=geojson inputs/wedrawthelines/cd-2020.json
    tippecanoe -f -l cd-2020 -o outputs/cd-2020.pmtiles --maximum-zoom=14 --minimum-zoom=4 inputs/wedrawthelines/cd-2020.json
    rm -rf inputs/wedrawthelines/cd-2020.json inputs/wedrawthelines/CD_Final\ shapefile

    unzip -o inputs/prop50/AB604.zip -d inputs/prop50/
    npx mapshaper inputs/prop50/AB604/AB604.shp -proj wgs84 int=ESPG:4269 -o format=geojson inputs/prop50/AB604.json
    tippecanoe -f -l cd-prop50 -o outputs/cd-prop50.pmtiles --maximum-zoom=14 --minimum-zoom=4 inputs/prop50/AB604.json
    rm -rf inputs/prop50/AB604.json inputs/prop50/AB604

    tile-join --force -o outputs/congressional.pmtiles outputs/cd-2020.pmtiles outputs/cd-prop50.pmtiles
    rm outputs/cd-2020.pmtiles outputs/cd-prop50.pmtiles

generate-demographics-pmtiles:
    npx mapshaper outputs/precinct_results_plus_demographics.geojson -proj wgs84 init=EPSG:3310 -o format=geojson ndjson outputs/precinct_results_plus_demographics_nd.json
    tippecanoe -f -l precincts -o outputs/precinct_results_plus_demographics.pmtiles --maximum-zoom=14 --minimum-zoom=4 --read-parallel outputs/precinct_results_plus_demographics_nd.json
