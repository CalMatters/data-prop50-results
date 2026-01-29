<script>
	// Svelte Components
	import Credits from '$lib/components/ui/Credits.svelte';
	import Header from '$lib/components/ui/Header.svelte';
	import MapLibreMap from '$lib/components/maps/MapLibreMap.svelte';
	// this is a JS object that should form the basis of what you
	// pass as the `style` prop to <MapLibreMap />
	// it isn't loaded by default so that you can place your data
	// layer where it makes the most sense
	import mapLibreStyle from '$lib/components/maps/map-libre-style.js';
	import maplibregl from 'maplibre-gl';

	// --- precinct layer config ---
	// Put your PMTiles file here:
	//   vis/static/precinct_results_plus_demographics.pmtiles
	// It will be served at:
	//   /precinct_results_plus_demographics.pmtiles
	const PRECINCT_PMTILES_URL =
		'pmtiles:///precinct_results_plus_demographics_with_congressional.pmtiles';
	const PRECINCT_SOURCE_ID = 'precincts';
	// If nothing renders, this is the *first* thing to change:
	// it must match the tippecanoe `-l <LAYER_NAME>` you used.
	const PRECINCT_SOURCE_LAYER = 'precincts';

	const ADDRESS_LABEL_LAYER_NAME = 'address_label';

	const CD_2020_FILL = '#643B80';
	const CD_PROP50_FILL = '#386F1F';

	// if you want to change something about the map then we should use
	// a component-level variable, in this case we'll call it map
	let map = null;
</script>

<main class="graphic">
	<Header
		title="Precinct Results and Demographics with congressional districts"
		copy="Explore voting results and demographic data by precinct. Colors represent the majority racial group in each precinct based on Census American Community Survey Citizen Voting Age Population (CVAP) data."
		size="inline"
	/>

	<section class="legend">
		<p class="legend-title">Congressional districts</p>
		<div class="legend-items">
			<div class="legend-item">
				<div class="color-box" style="background-color: {CD_2020_FILL};"></div>
				<button class="label">CD 2020</button>
			</div>
			<div class="legend-item">
				<div class="color-box" style="background-color: {CD_PROP50_FILL};"></div>
				<button class="label">CD PROP 50</button>
			</div>
		</div>

		<div class="saturation-note">
			<p class="legend-title">Yes %</p>
			<p class="note-text">
				Each color varies based on the percentage of "yes" votes in that precinct. More blue
				precincts indicate higher percentages of "yes" votes, darker red precincts indicate a lower
				percentages of "yes" votes, while lighter colors indicate a closer result.
			</p>
			<div class="saturation-example">
				<div class="gradient-bar">
					<div
						class="gradient-fill"
						style="background: linear-gradient(to right, #8E1F1B, #E7F0FE, #0A3258)"
					></div>
					<div class="midpoint-indicator" title="50% - Yes wins above this line"></div>
				</div>
				<div class="gradient-labels">
					<span>Yes losing</span>
					<span class="midpoint-label">50%</span>
					<span>Yes winning</span>
				</div>
			</div>
		</div>
	</section>

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
							attribution: 'Precinct results + demographics w/ congress districts'
						});
					}

					const insertBeforeLayerId = map
						.getStyle()
						?.layers?.find((l) => l.id === ADDRESS_LABEL_LAYER_NAME)?.id;

					if (!map.getLayer('precincts-fill')) {
						// Create fill-color expression that interpolates saturation based on yes_pct
						// Using exponential interpolation and very light colors at 0% for more dramatic contrast
						const fillColorExpression = [
							'interpolate',
							['linear'],
							['get', 'yes_pct'],
							0,
							'#8E1F1B', // Very light blue (almost white)
							50,
							'#E7F0FE', // Medium blue
							100,
							'#0A3258'
						];

						map.addLayer(
							{
								id: 'precincts-fill',
								type: 'fill',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
									// Conditional coloring based on yes_pct
									'fill-color': fillColorExpression,
									'fill-opacity': ['case', ['has', 'yes_pct'], 0.75, 0]
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
									'line-width': 0.1,
									'line-opacity': 0.3
								}
							},
							insertBeforeLayerId
						);
					}

					map.addLayer(
						{
							id: 'cd-2020-outline',
							type: 'line',
							source: PRECINCT_SOURCE_ID,
							'source-layer': 'cd-2020',
							paint: {
								'line-color': CD_2020_FILL,
								'line-width': 0.75,
								'line-opacity': 0.4
							}
						},
						insertBeforeLayerId
					);

					map.addLayer(
						{
							id: 'cd-prop50-outline',
							type: 'line',
							source: PRECINCT_SOURCE_ID,
							'source-layer': 'cd-prop50',
							paint: {
								'line-color': CD_PROP50_FILL,
								'line-width': 0.75,
								'line-opacity': 0.4
							}
						},
						insertBeforeLayerId
					);

					// Add click handler for popup
					const popup = new maplibregl.Popup({
						closeButton: true,
						closeOnClick: true
					});

					map.on('click', 'precincts-fill', (e) => {
						const feature = e.features[0];
						if (!feature) return;

						console.log(feature.properties);

						// Create popup HTML content
						const popupContent = `
							<div class="popup-content">
								<p class="popup-line"><strong>${feature.properties.precinct_id}</strong>, ${feature.properties.county} County</p>
								<p class="popup-line">Prop 50 received <strong>${feature.properties.yes_pct}%</strong> support</p>
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
		credit="Mo A, Jeremia K, CalMatters"
		source="Election results and precinct geographies are compiled from county election administrators. Congressional boundaries come from the indepedent redistricting commission and the state legislature."
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
	.legend {
		margin: 16px 0;
		padding: 16px;
		background-color: var(--aqua_100);
		border-radius: 4px;
		font-family: var(--font-family);

		@media screen and (max-width: 767px) {
			padding: 12px;
		}
	}

	.legend-title {
		margin: 0 0 12px 0;
		font-weight: 700;
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
	}

	.legend-items {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		margin-bottom: 20px;

		@media screen and (max-width: 767px) {
			gap: 12px;
		}
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.legend-item button {
		background-color: transparent;
		padding: inherit;
		appearance: none;
	}

	.legend-item button:hover {
		background-color: white;
	}

	.color-box {
		width: 20px;
		height: 20px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.label {
		margin: 0;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_600);
	}

	.saturation-note {
		margin-top: 20px;
		padding-top: 20px;
		border-top: 1px solid var(--gray_200);
	}

	.note-title {
		margin: 0 0 8px 0;
		font-weight: 700;
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
	}

	.note-text {
		margin: 0 0 12px 0;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_400);
	}

	.saturation-example {
		margin-top: 12px;
	}

	.gradient-bar {
		position: relative;
		width: 100%;
		height: 24px;
		border-radius: 4px;
		overflow: visible;
		margin-bottom: 6px;
		border: 1px solid var(--gray_200);
	}

	.gradient-fill {
		width: 100%;
		height: 100%;
		border-radius: 4px;
	}

	.midpoint-indicator {
		position: absolute;
		left: 50%;
		top: 0;
		bottom: 0;
		width: 2px;
		background-color: var(--gray_600);
		transform: translateX(-50%);
		z-index: 1;
		box-shadow: 0 0 2px rgba(0, 0, 0, 0.2);
	}

	.gradient-labels {
		display: flex;
		justify-content: space-between;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_400);
		position: relative;
	}

	.midpoint-label {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		font-weight: 600;
		color: var(--gray_600);
	}
</style>
