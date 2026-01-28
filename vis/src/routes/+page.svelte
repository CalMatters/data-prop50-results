<script>
	// Svelte Components
	import Credits from '$lib/components/ui/Credits.svelte';
	import Header from '$lib/components/ui/Header.svelte';
	import MapLibreMap from '$lib/components/maps/MapLibreMap.svelte';
	import ElectionResultsLegend from '$lib/components/ui/ElectionResultsLegend.svelte';
	import RacialGroupRadioSelector from '$lib/components/ui/RacialGroupRadioSelector.svelte';

	// this is a JS object that should form the basis of what you
	// pass as the `style` prop to <MapLibreMap />
	// it isn't loaded by default so that you can place your data
	// layer where it makes the most sense
	import mapLibreStyle from '$lib/components/maps/map-libre-style.js';
	import maplibregl from 'maplibre-gl';
	import { normalizeRacialGroup } from '$lib/racial-group-colors.js';

	// --- precinct layer config ---
	// Put your PMTiles file here:
	//   vis/static/precinct_results_plus_demographics.pmtiles
	// It will be served at:
	//   /precinct_results_plus_demographics.pmtiles
	const PRECINCT_PMTILES_URL = 'pmtiles:///precinct_results_plus_demographics.pmtiles';
	const PRECINCT_SOURCE_ID = 'precincts';
	// If nothing renders, this is the *first* thing to change:
	// it must match the tippecanoe `-l <LAYER_NAME>` you used.
	const PRECINCT_SOURCE_LAYER = 'precincts';

	const ADDRESS_LABEL_LAYER_NAME = 'address_label';

	// Black highlight color for increased visibility
	const HIGHLIGHT_COLOR = '#000000';
	const DEFAULT_OUTLINE_COLOR = '#ffffff';
	const DEFAULT_OUTLINE_WIDTH = 0.75;
	const HIGHLIGHT_OUTLINE_WIDTH = 2.5; // Thicker to dominate over white borders

	// if you want to change something about the map then we should use
	// a component-level variable, in this case we'll call it map
	let map = null;
	let selectedRacialGroup = $state(null);

	// Function to update the highlight outline layer based on selected racial group
	function updateOutlineLayer(selectedGroup) {
		if (!map) {
			console.warn('Map not available for updateOutlineLayer');
			return;
		}
		
		if (!map.getLayer('precincts-outline-highlight')) {
			console.warn('precincts-outline-highlight layer not available');
			return;
		}

		if (selectedGroup === null) {
			// Hide the highlight layer when no group is selected
			map.setLayoutProperty('precincts-outline-highlight', 'visibility', 'none');
			// Restore white border opacity to normal
			if (map.getLayer('precincts-outline')) {
				map.setPaintProperty('precincts-outline', 'line-opacity', 0.6);
			}
		} else {
			// Show the highlight layer and set filter to match selected group
			map.setLayoutProperty('precincts-outline-highlight', 'visibility', 'visible');
			
			// Reduce white border opacity to make black borders stand out more
			if (map.getLayer('precincts-outline')) {
				map.setPaintProperty('precincts-outline', 'line-opacity', 0.3);
			}
			
			// Create filter expression to only show matching precincts
			let filterExpression;

			if (selectedGroup === 'Multiracial') {
				// For Multiracial, check if the group starts with "Multiracial"
				filterExpression = [
					'any',
					['==', ['get', 'majority_racial_group'], 'Multiracial'],
					['==', ['slice', ['get', 'majority_racial_group'], 0, 11], 'Multiracial']
				];
			} else {
				// For other groups, simple equality check
				filterExpression = ['==', ['get', 'majority_racial_group'], selectedGroup];
			}

			map.setFilter('precincts-outline-highlight', filterExpression);
		}
	}

	// Function to handle racial group selection changes
	function handleRacialGroupSelect(group) {
		selectedRacialGroup = group;
		// Update map immediately when selection changes
		updateOutlineLayer(group);
	}

	// Reactive effect as backup to update map when selection or map changes
	$effect(() => {
		if (map && selectedRacialGroup !== undefined) {
			updateOutlineLayer(selectedRacialGroup);
		}
	});
</script>

<main class="graphic">
	<Header
		title="Precinct Results and Demographics"
		copy="Explore voting results and demographic data by precinct. Colors represent the majority racial group in each precinct based on Census American Community Survey Citizen Voting Age Population (CVAP) data. Select a racial group below to highlight matching precincts with black borders."
		size="inline"
	/>

	<ElectionResultsLegend />

	<RacialGroupRadioSelector
		selectedGroup={selectedRacialGroup}
		onSelect={handleRacialGroupSelect}
	/>

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

					const insertBeforeLayerId = map.getStyle()?.layers?.find((l) => l.id === ADDRESS_LABEL_LAYER_NAME)?.id;

					if (!map.getLayer('precincts-fill')) {
						// Linear diverging gradient based on yes_pct
						// Red at 0% (no votes), light gray at 50% (neutral), blue at 100% (yes votes)
						const fillColorExpression = [
							'interpolate',
							['linear'],
							['coalesce', ['get', 'yes_pct'], 50], // Default to 50% (neutral) if missing
							0, '#D35F4F',   // Red at 0% (no votes) --red_500
							50, '#EEEEEE',  // Light gray at 50% (neutral) --gray_100
							100, '#5B92CE'  // Blue at 100% (yes votes) --blue_500
						];

						map.addLayer(
							{
								id: 'precincts-fill',
								type: 'fill',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
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
									'line-color': DEFAULT_OUTLINE_COLOR,
									'line-width': DEFAULT_OUTLINE_WIDTH,
									'line-opacity': 0.6
								}
							},
							insertBeforeLayerId
						);
					}

					// Add highlight layer on top of the white outline layer
					// Insert it right after 'precincts-outline' so it renders on top
					if (!map.getLayer('precincts-outline-highlight')) {
						map.addLayer(
							{
								id: 'precincts-outline-highlight',
								type: 'line',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								filter: ['==', ['get', 'majority_racial_group'], ''],
								paint: {
									'line-color': HIGHLIGHT_COLOR,
									'line-width': HIGHLIGHT_OUTLINE_WIDTH,
									'line-opacity': 1
								},
								layout: {
									visibility: 'none'
								}
							},
							insertBeforeLayerId
						);
						
						// Ensure highlight layer renders on top of white outline
						// Move it to be right after 'precincts-outline' by removing and re-adding
						if (map.getLayer('precincts-outline')) {
							// Get the current layer configuration
							const highlightLayer = map.getStyle().layers.find(l => l.id === 'precincts-outline-highlight');
							if (highlightLayer) {
								// Remove the layer
								map.removeLayer('precincts-outline-highlight');
								// Re-add it after 'precincts-outline' so it renders on top
								// Using 'precincts-outline' as beforeId means it will be inserted right after it
								map.addLayer({
									id: 'precincts-outline-highlight',
									type: 'line',
									source: PRECINCT_SOURCE_ID,
									'source-layer': PRECINCT_SOURCE_LAYER,
									filter: ['==', ['get', 'majority_racial_group'], ''],
									paint: {
										'line-color': HIGHLIGHT_COLOR,
										'line-width': HIGHLIGHT_OUTLINE_WIDTH,
										'line-opacity': 1
									},
									layout: {
										visibility: 'none'
									}
								}, 'precincts-outline');
							}
						}
					}

					// Initialize outline layer styling based on current selection
					updateOutlineLayer(selectedRacialGroup);

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
						const groupPctFormatted = majorityGroupPct != null 
							? Math.round(majorityGroupPct) 
							: 'N/A';
						const yesPctFormatted = yesPct != null 
							? Math.round(yesPct) 
							: 'N/A';

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

						popup
							.setLngLat(e.lngLat)
							.setHTML(popupContent)
							.addTo(map);
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
