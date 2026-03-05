<script>
	// Svelte Components
	import CountySelect from '$lib/components/ui/CountySelect.svelte';
	import Credits from '$lib/components/ui/Credits.svelte';
	import Header from '$lib/components/ui/Header.svelte';
	import MapLibreMap from '$lib/components/maps/MapLibreMap.svelte';
	import PrecinctSelect from '$lib/components/ui/PrecinctSelect.svelte';
	import RacialGroupLegend from '$lib/components/ui/RacialGroupLegend.svelte';
	import { onMount } from 'svelte';

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

	/** Saturation metric for precinct fill: 'yes_pct' (0–100), 'vote_shift' (±15%), or 'flipped' (R/D vs no flip). */
	let saturationMetric = $state('yes_pct');

	// Shared vote_shift (and flipped) color stops
	const VOTE_SHIFT_GROUP_COLORS = {
		White: { v0: '#E8F2FA', v1: '#9BC0E0', v2: RACIAL_GROUP_COLORS['White'] },
		Multiracial: { v0: '#F0E8F7', v1: '#C9A5E1', v2: RACIAL_GROUP_COLORS['Multiracial'] },
		'Hispanic Or Latino': {
			v0: '#FBF0E5',
			v1: '#F2B872',
			v2: RACIAL_GROUP_COLORS['Hispanic Or Latino']
		},
		'Black Or African American': {
			v0: '#E8F5E3',
			v1: '#8DCC6F',
			v2: RACIAL_GROUP_COLORS['Black Or African American']
		},
		Asian: { v0: '#FAE8E6', v1: '#E18A7F', v2: RACIAL_GROUP_COLORS['Asian'] }
	};
	const RACIAL_GROUP_ORDER = [
		'White',
		'Multiracial',
		'Hispanic Or Latino',
		'Black Or African American',
		'Asian'
	];

	/**
	 * Build a MapLibre 'case' expression: for each racial group, output one color; default fallback last.
	 * Used by both vote_shift (interpolated) and flipped (discrete) so we stay DRY.
	 * @param {Array} normalizedGroupExpr - MapLibre expression that evaluates to the group name
	 * @param {'v0' | 'v1' | 'v2'} shade - Which shade from VOTE_SHIFT_GROUP_COLORS (v0=light, v2=dark)
	 * @returns {Array} MapLibre expression
	 */
	function buildGroupToColorCase(normalizedGroupExpr, shade) {
		return [
			'case',
			...RACIAL_GROUP_ORDER.flatMap((group) => [
				['==', normalizedGroupExpr, group],
				VOTE_SHIFT_GROUP_COLORS[group][shade]
			]),
			RACIAL_GROUP_COLORS[null]
		];
	}

	let { data } = $props();
	let { county } = data;

	// if you want to change something about the map then we should use
	// a component-level variable, in this case we'll call it map
	let map = $state(null);
	let selectedCounty = $state(null);
	let selectedPrecinctId = $state(null);
	/** County name → list of precinct IDs (from /county_precincts.json) */
	let countyPrecincts = $state(/** @type {Record<string, string[]>} */ ({}));

	onMount(async () => {
		const res = await fetch('/county_precincts.json');
		if (res.ok) countyPrecincts = await res.json();
	});

	// Normalized racial group expression (same for all metrics)
	const normalizedGroup = [
		'coalesce',
		[
			'case',
			['has', 'majority_racial_group'],
			[
				'case',
				['==', ['slice', ['get', 'majority_racial_group'], 0, 11], 'Multiracial'],
				'Multiracial',
				['get', 'majority_racial_group']
			],
			'__null__'
		],
		'__null__'
	];

	/**
	 * Build MapLibre fill-color expression for precincts by metric.
	 * - yes_pct: interpolate 0–100% → light to dark by racial group.
	 * - vote_shift: interpolate −15 to +15% → light to dark (same palette as flipped).
	 * - flipped: grey when no flip; D flip = dark (v2), R flip = light (v0), by group.
	 * @param {'yes_pct' | 'vote_shift' | 'flipped'} metric
	 */
	function buildPrecinctFillColorExpression(metric) {
		// Flipped: three discrete outcomes; reuse vote_shift shades for consistency.
		if (metric === 'flipped') {
			const flippedProp = ['get', 'flipped'];
			const isFlippedDOrR = ['in', ['coalesce', flippedProp, ''], ['literal', ['D', 'R']]];

			return [
				'case',
				['!', isFlippedDOrR],
				RACIAL_GROUP_COLORS[null],
				['==', flippedProp, 'D'],
				buildGroupToColorCase(normalizedGroup, 'v2'),
				buildGroupToColorCase(normalizedGroup, 'v0')
			];
		}

		const isYesPct = metric === 'yes_pct';
		const value = isYesPct
			? ['coalesce', ['get', 'yes_pct'], 0]
			: ['coalesce', ['get', 'vote_shift'], 0];
		const stops = isYesPct ? [0, 50, 100] : [-15, 0, 15];

		const branches = isYesPct
			? [
					['==', normalizedGroup, 'White'],
					[
						'interpolate',
						['exponential', 1.5],
						value,
						stops[0],
						'#E8F2FA',
						stops[1],
						'#9BC0E0',
						stops[2],
						RACIAL_GROUP_COLORS['White']
					],
					['==', normalizedGroup, 'Multiracial'],
					[
						'interpolate',
						['exponential', 1.5],
						value,
						stops[0],
						'#F0E8F7',
						stops[1],
						'#C9A5E1',
						stops[2],
						RACIAL_GROUP_COLORS['Multiracial']
					],
					['==', normalizedGroup, 'Hispanic Or Latino'],
					[
						'interpolate',
						['exponential', 1.5],
						value,
						stops[0],
						'#FBF0E5',
						stops[1],
						'#F2B872',
						stops[2],
						RACIAL_GROUP_COLORS['Hispanic Or Latino']
					],
					['==', normalizedGroup, 'Black Or African American'],
					[
						'interpolate',
						['exponential', 1.5],
						value,
						stops[0],
						'#E8F5E3',
						stops[1],
						'#8DCC6F',
						stops[2],
						RACIAL_GROUP_COLORS['Black Or African American']
					],
					['==', normalizedGroup, 'Asian'],
					[
						'interpolate',
						['exponential', 1.5],
						value,
						stops[0],
						'#FAE8E6',
						stops[1],
						'#E18A7F',
						stops[2],
						RACIAL_GROUP_COLORS['Asian']
					]
				]
			: RACIAL_GROUP_ORDER.flatMap((group) => {
					const colors = VOTE_SHIFT_GROUP_COLORS[group];
					return [
						['==', normalizedGroup, group],
						[
							'interpolate',
							['exponential', 1.5],
							value,
							stops[0],
							colors.v0,
							stops[1],
							colors.v1,
							stops[2],
							colors.v2
						]
					];
				});

		return ['case', ...branches, RACIAL_GROUP_COLORS[null]];
	}

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

	$effect(() => {
		if (!map || !map.getLayer('precincts-fill')) return;
		map.setPaintProperty(
			'precincts-fill',
			'fill-color',
			buildPrecinctFillColorExpression(saturationMetric)
		);
	});

	$effect(() => {
		if (!map || !map.getLayer('selected-precinct-outline')) return;
		const filter =
			selectedCounty && selectedPrecinctId
				? [
						'all',
						['==', ['get', 'county'], selectedCounty.COUNTY_NAME],
						['==', ['get', 'precinct_id'], selectedPrecinctId]
					]
				: ['==', ['get', 'precinct_id'], ''];
		map.setFilter('selected-precinct-outline', filter);
	});
</script>

<main class="graphic">
	<Header
		title="Precinct Results and Demographics"
		copy="Explore voting results and demographic data by precinct. Colors represent the majority racial group in each precinct based on Census American Community Survey Citizen Voting Age Population (CVAP) data."
		size="inline"
	/>

	<CountySelect
		initialValue={county}
		label="Selected county"
		onchange={(county) => {
			selectedCounty = counties.find((d) => d.COUNTY_NAME.toLowerCase() === county?.toLowerCase());
			selectedPrecinctId = null;
		}}
	/>

	{#if selectedCounty}
		<PrecinctSelect
			precinctIds={countyPrecincts[selectedCounty.COUNTY_NAME] ?? []}
			{selectedPrecinctId}
			onchange={(id) => (selectedPrecinctId = id)}
			label="Selected precinct"
		/>
	{/if}

	<RacialGroupLegend {saturationMetric} onSaturationMetricChange={(v) => (saturationMetric = v)} />

	<section>
		<MapLibreMap
			load={(m) => {
				map = m;

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
						map.addLayer(
							{
								id: 'precincts-fill',
								type: 'fill',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
									'fill-color': buildPrecinctFillColorExpression('yes_pct'),
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

					// Selected precinct outline (on top of precincts-outline, below county bounds)
					if (!map.getLayer('selected-precinct-outline')) {
						map.addLayer(
							{
								id: 'selected-precinct-outline',
								type: 'line',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								filter: ['==', ['get', 'precinct_id'], ''],
								paint: {
									'line-color': SELECTED_COUNTY_STROKE_COLOR,
									'line-width': SELECTED_COUNTY_STROKE_WIDTH,
									'line-opacity': 0.7
								}
							},
							'county-bounds-line'
						);
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
						const voteShift = feature.properties.vote_shift;
						const flipped = feature.properties.flipped;

						// Format the percentage values
						const groupPctFormatted =
							majorityGroupPct != null ? Math.round(majorityGroupPct) : 'N/A';
						const yesPctFormatted = yesPct != null ? Math.round(yesPct) : 'N/A';
						const voteShiftFormatted =
							voteShift != null ? `${voteShift >= 0 ? '+' : ''}${Math.round(voteShift)}` : null;

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

						// Flip status line
						const flipLine =
							flipped === 'D'
								? 'Flipped: Trump 2024 → Yes on Prop 50'
								: flipped === 'R'
									? 'Flipped: Harris 2024 → No on Prop 50'
									: '';

						// Create popup HTML content
						const supportLine =
							voteShiftFormatted != null
								? `Prop 50 received <strong>${yesPctFormatted}%</strong> support; <strong>${voteShiftFormatted}%</strong> compared to Harris in 2024`
								: `Prop 50 received <strong>${yesPctFormatted}%</strong> support`;
						const popupContent = `
							<div class="popup-content">
								<p class="popup-line"><strong>${groupLabel}</strong> majority precinct</p>
								<p class="popup-line">${supportLine}</p>
								<p class="popup-line">${flipLine}</p>
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
		allowEmbed={false}
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
