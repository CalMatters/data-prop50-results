<script>
	// Svelte Components
	import CountySelect from '$lib/components/ui/CountySelect.svelte';
	import Credits from '$lib/components/ui/Credits.svelte';
	import Header from '$lib/components/ui/Header.svelte';
	import MapLibreMap from '$lib/components/maps/MapLibreMap.svelte';
	import RacialGroupLegend from '$lib/components/ui/RacialGroupLegend.svelte';

	// this is the bounding boxes of each county
	import counties from '$lib/ca-county-bounding-boxes.json';

	// this is a JS object that should form the basis of what you
	// pass as the `style` prop to <MapLibreMap />
	// it isn't loaded by default so that you can place your data
	// layer where it makes the most sense
	import mapLibreStyle from '$lib/components/maps/map-libre-style.js';
	import { RACIAL_GROUP_COLORS } from '$lib/racial-group-colors.js';
	import maplibregl from 'maplibre-gl';

	// --- precinct layer config ---
	// Put your PMTiles file here:
	//   vis/static/precinct_results_plus_demographics.pmtiles
	// It will be served at:
	//   /precinct_results_plus_demographics.pmtiles
	const PRECINCT_PMTILES_URL = 'pmtiles:///precinct_results_plus_demographics_blocks.pmtiles';
	const PRECINCT_SOURCE_ID = 'precincts';
	// If nothing renders, this is the *first* thing to change:
	// it must match the tippecanoe `-l <LAYER_NAME>` you used.
	const PRECINCT_SOURCE_LAYER = 'precincts';

	const ADDRESS_LABEL_LAYER_NAME = 'address_label';

	// County bounds for subtle border stroke (vis/static/county_bounds.geojson)
	const COUNTY_BOUNDS_SOURCE_ID = 'county-bounds';
	const COUNTY_BOUNDS_URL = '/county_bounds.geojson';

	// Color for selected county boundary
	const SELECTED_COUNTY_STROKE_COLOR = '#212121';
	const SELECTED_COUNTY_STROKE_WIDTH = 2;

	let { data } = $props();
	let { county } = data;

	// if you want to change something about the map then we should use
	// a component-level variable, in this case we'll call it map
	let map = $state(null);
	let selectedCounty = $state(null);

	function zoomToAndHighlightSelectedCounty() {
		// create a bbox for the selected county
		const bbox = [
			[selectedCounty?.xmin, selectedCounty?.ymin],
			[selectedCounty?.xmax, selectedCounty?.ymax]
		];

		// set the map to those boundaries
		map.fitBounds(bbox, { padding: 40 });

		// use a maplibre expression to only show the border
		// of the selected county
		// https://maplibre.org/maplibre-style-spec/expressions/
		map.setPaintProperty('selected-county-bounds-line', 'line-width', [
			'case',
			['==', ['get', 'NAME'], selectedCounty.COUNTY_NAME],
			SELECTED_COUNTY_STROKE_WIDTH,
			0
		]);
	}

	$effect(() => {
		// check for variables and declare dependencies at the
		// same time - https://svelte.dev/docs/svelte/$effect
		if (!map || !selectedCounty) return;

		zoomToAndHighlightSelectedCounty();
	});
</script>

<main class="graphic">
	<Header
		title="Precinct Results and Demographics"
		copy="<p><strong>currently using win margin of prop 50 for arrow</strong></p>Explore voting results and demographic data by precinct. Colors represent the majority racial group in each precinct based on Census American Community Survey Citizen Voting Age Population (CVAP) data."
		size="inline"
	/>

	<CountySelect
		initialValue={county}
		label="Selected county"
		onchange={(county) => {
			selectedCounty = counties.find((d) => d.COUNTY_NAME.toLowerCase() === county?.toLowerCase());
		}}
	/>

	<RacialGroupLegend />

	<section>
		<MapLibreMap
			load={async (m) => {
				map = m;

				const image = await map.loadImage('/arrow.png');
				map.addImage('arrow', image.data);

				// Add precinct source + layers on top of the basemap style.
				// This is intentionally minimal so you can iterate quickly.
				try {
					if (!map.getSource(PRECINCT_SOURCE_ID)) {
						map.addSource(PRECINCT_SOURCE_ID, {
							type: 'vector',
							url: PRECINCT_PMTILES_URL,
							attribution: 'Precinct results + demographics'
						});
					}

					const insertBeforeLayerId = map
						.getStyle()
						?.layers?.find((l) => l.id === ADDRESS_LABEL_LAYER_NAME)?.id;

					if (!map.getLayer('precincts-fill')) {
						// Build fill-color expression using colors from guide.scss CSS variables
						// Colors are explicitly sourced from RACIAL_GROUP_COLORS which references guide.scss
						// Saturation varies based on yes_pct (0-100): higher yes_pct = higher saturation

						// Normalize racial group first
						const normalizedGroup = [
							'coalesce',
							[
								'case',
								['has', 'majority_racial_group'],
								[
									'case',
									// Check if string starts with "Multiracial" by comparing first 11 characters
									['==', ['slice', ['get', 'majority_racial_group'], 0, 11], 'Multiracial'],
									'Multiracial',
									['get', 'majority_racial_group']
								],
								'__null__'
							],
							'__null__'
						];

						// Get yes_pct value (default to 0 if missing)
						const yesPct = ['coalesce', ['get', 'yes_pct'], 0];

						// Create fill-color expression that interpolates saturation based on yes_pct
						// Using exponential interpolation and very light colors at 0% for more dramatic contrast
						const fillColorExpression = [
							'case',
							// White: interpolate from very light blue to saturated blue
							['==', normalizedGroup, 'White'],
							[
								'interpolate',
								['exponential', 1.5],
								yesPct,
								0,
								'#E8F2FA', // Very light blue (almost white)
								50,
								'#9BC0E0', // Medium blue
								100,
								RACIAL_GROUP_COLORS['White'] // Full saturation blue_500
							],
							// Multiracial: interpolate from very light violet to saturated violet
							['==', normalizedGroup, 'Multiracial'],
							[
								'interpolate',
								['exponential', 1.5],
								yesPct,
								0,
								'#F0E8F7', // Very light violet (almost white)
								50,
								'#C9A5E1', // Medium violet
								100,
								RACIAL_GROUP_COLORS['Multiracial'] // Full saturation violet_500
							],
							// Hispanic Or Latino: interpolate from very light orange to saturated orange
							['==', normalizedGroup, 'Hispanic Or Latino'],
							[
								'interpolate',
								['exponential', 1.5],
								yesPct,
								0,
								'#FBF0E5', // Very light orange (almost white)
								50,
								'#F2B872', // Medium orange
								100,
								RACIAL_GROUP_COLORS['Hispanic Or Latino'] // Full saturation orange_500
							],
							// Black Or African American: interpolate from very light green to saturated green
							['==', normalizedGroup, 'Black Or African American'],
							[
								'interpolate',
								['exponential', 1.5],
								yesPct,
								0,
								'#E8F5E3', // Very light green (almost white)
								50,
								'#8DCC6F', // Medium green
								100,
								RACIAL_GROUP_COLORS['Black Or African American'] // Full saturation green_500
							],
							// Asian: interpolate from very light red to saturated red
							['==', normalizedGroup, 'Asian'],
							[
								'interpolate',
								['exponential', 1.5],
								yesPct,
								0,
								'#FAE8E6', // Very light red (almost white)
								50,
								'#E18A7F', // Medium red
								100,
								RACIAL_GROUP_COLORS['Asian'] // Full saturation red_500
							],
							// Default: grey for null/unknown values
							RACIAL_GROUP_COLORS[null]
						];

						map.addLayer(
							{
								id: 'precincts-fill',
								type: 'fill',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
									// Conditional coloring based on majority_racial_group
									'fill-color': fillColorExpression,
									'fill-opacity': 0.75
								}
							},
							insertBeforeLayerId
						);
					}

					if (!map.getLayer('precincts-outline')) {
						map.addLayer(
							{
								id: 'precincts-outline',
								type: 'line',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
									'line-color': '#ffffff',
									'line-width': 0.75,
									'line-opacity': 0.6
								}
							},
							insertBeforeLayerId
						);
					}

					// County borders (subtle stroke on top of precincts)
					if (!map.getSource(COUNTY_BOUNDS_SOURCE_ID)) {
						map.addSource(COUNTY_BOUNDS_SOURCE_ID, {
							type: 'geojson',
							data: COUNTY_BOUNDS_URL
						});
					}
					if (!map.getLayer('county-bounds-line')) {
						map.addLayer(
							{
								id: 'county-bounds-line',
								type: 'line',
								source: COUNTY_BOUNDS_SOURCE_ID,
								paint: {
									'line-color': 'rgba(120, 120, 120, 0.5)',
									'line-width': 0.75,
									'line-opacity': 0.7
								}
							},
							insertBeforeLayerId
						);
					}

					if (!map.getLayer('selected-county-bounds-line')) {
						map.addLayer(
							{
								id: 'selected-county-bounds-line',
								type: 'line',
								source: COUNTY_BOUNDS_SOURCE_ID,
								paint: {
									'line-color': SELECTED_COUNTY_STROKE_COLOR,
									'line-width': [
										'case',
										['==', ['get', 'NAME'], 'NULL'],
										SELECTED_COUNTY_STROKE_WIDTH,
										0
									],
									'line-opacity': 0.7
								}
							},
							insertBeforeLayerId
						);
					}

					if (!map.getLayer('precincts-shift-arrow')) {
						map.addLayer({
							id: 'precincts-shift-arrow',
							type: 'symbol',
							source: PRECINCT_SOURCE_ID,
							'source-layer': PRECINCT_SOURCE_LAYER,
							layout: {
								'icon-image': 'arrow',
								'icon-overlap': 'always',
								'icon-rotate': ['case', ['<', ['get', 'vote_shift'], 0], -10, -170],
								'icon-size': ['case',
									['has', 'vote_shift'],
									['/', ['abs', ['get', 'vote_shift']], 500],
									0
								]
									// '/', ['abs', ['get', 'vote_shift']], 1000],
							},
							paint: {
								'icon-opacity': 0.8
							}
						});
					}

					// Add click handler for popup
					const popup = new maplibregl.Popup({
						closeButton: true,
						closeOnClick: true
					});

					map.on('click', 'precincts-fill', (e) => {
						const feature = e.features[0];
						if (!feature) return;

						// Get data from feature properties
						const majorityGroup = feature.properties.majority_racial_group;
						const majorityGroupPct = feature.properties.majority_racial_group_pct;
						const yesPct = feature.properties.yes_pct;

						// Format the percentage values
						const groupPctFormatted =
							majorityGroupPct != null ? Math.round(majorityGroupPct) : 'N/A';
						const yesPctFormatted = yesPct != null ? Math.round(yesPct) : 'N/A';

						// Format the group label - for multiracial, move percentage into parentheses
						let groupLabel;
						if (majorityGroup && majorityGroup.startsWith('Multiracial')) {
							// Parse "Multiracial (X plurality)" and add percentage
							const match = majorityGroup.match(/^Multiracial \((.+?)\)$/);
							if (match) {
								const pluralityGroup = match[1];
								groupLabel = `Multiracial (${pluralityGroup} ${groupPctFormatted}%)`;
							} else {
								groupLabel = `${majorityGroup} ${groupPctFormatted}%`;
							}
						} else {
							groupLabel = `${majorityGroup || 'Unknown'} (${groupPctFormatted}%)`;
						}

						// Create popup HTML content
						const popupContent = `
							<div class="popup-content">
								<p class="popup-line"><strong>${groupLabel}</strong> majority precinct</p>
								<p class="popup-line">Prop 50 received <strong>${yesPctFormatted}%</strong> support</p>
							</div>
						`;

						popup.setLngLat(e.lngLat).setHTML(popupContent).addTo(map);
					});

					// Change cursor on hover
					map.on('mouseenter', 'precincts-fill', () => {
						map.getCanvas().style.cursor = 'pointer';
					});

					map.on('mouseleave', 'precincts-fill', () => {
						map.getCanvas().style.cursor = '';
					});
				} catch (err) {
					console.error('Failed to add precinct layers:', err);
				}
			}}
			style={mapLibreStyle}
		/>
	</section>

	<Credits
		credit="Mo A, CalMatters"
		source="Election results and precinct geographies are compiled from county election administrators. Racial demographic data is Census American Community Survey Citizen Voting Age Population (CVAP) data."
		note="No pixels were harmed in the creation of this example route."
	/>
</main>

<!-- pym likes to cut off the last 40 or so pixels -->
<div style="height:40px;"></div>

<style lang="scss">
	main {
		max-width: 780px;
		margin: 0 auto;
	}

	:global(.maplibregl-popup-content) {
		font-family: var(--font-family);
		padding: 12px;
	}

	:global(.popup-content) {
		.popup-line {
			margin: 0 0 8px 0;
			font-size: var(--footnote-size);
			line-height: var(--footnote-height);
			color: var(--gray_600);

			&:last-child {
				margin-bottom: 0;
			}

			strong {
				font-weight: 600;
			}
		}
	}
</style>
