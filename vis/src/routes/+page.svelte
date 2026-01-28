<script>
	// Svelte Components
	import Credits from '$lib/components/ui/Credits.svelte';
	import Header from '$lib/components/ui/Header.svelte';
	import Callout from '$lib/components/Callout.svelte';
	import CallToActionBox from '$lib/components/CallToActionBox.svelte';
	import AlertBox from '$lib/components/ui/alert/AlertBox.svelte';
	import MapLibreMap from '$lib/components/maps/MapLibreMap.svelte';

	// this is a JS object that should form the basis of what you
	// pass as the `style` prop to <MapLibreMap />
	// it isn't loaded by default so that you can place your data
	// layer where it makes the most sense
	import mapLibreStyle from '$lib/components/maps/map-libre-style.js';

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

	// if you want to change something about the map then we should use
	// a component-level variable, in this case we'll call it map
	let map = null;

	// Dependencies
	import { onMount } from 'svelte';

	/** 
    /* Show Call to Action component
    /* @type {boolean}  
    */
	const activateCta = true;

	/** 
    /* Show Callout component
    /* @type {boolean}  
    */
	const activateCallout = true;

	/** 
    /* If calling an external API, store response here
    /* @type {Array}  
    */
	let apiContents = $state.raw([]);

	/** 
    /* Tracks whether API call is finished and successful in order to mount components, if necessary
    /* @type {boolean}  
    */
	let apiDataReady = $state(false);

	/**
	 * Fetch data from route and store in apiContents
	 * @param {string} route url to fetch
	 */
	async function makeApiCall(route) {
		try {
			const response = await fetch(`${route}`);
			if (response.ok) {
				apiContents = await response.json();
				apiDataReady = true;
			} else {
				console.log(`Failed to fetch ${route}.json.`);
			}
		} catch (error) {
			console.log(`Network error loading ${route}.json.`);
		}
	}

	onMount(async () => {
		await makeApiCall('/api/data');
		console.log(apiContents);
	});
</script>

<main class="graphic">
	<Header
		title="This is the headline for the graphic"
		copy="If there is any supporting context or other information that's important to know before digesting the graphic, this is where it goes."
		size="inline"
	/>

	<AlertBox type="info" text="Did you know I exist now? I feel so <strong>ALIVE</strong>!" />

	<section>
		<!-- main contents of graphic here -->

		{#if apiDataReady}
			<!-- do something with the data from the api once it's loaded -->
		{/if}

		<button
			onclick={() => {
				map.setPaintProperty('water', 'fill-color', '#0a819f');
			}}>Change water back to blue</button
		>
		<!--  -->
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
						map.addLayer(
							{
								id: 'precincts-fill',
								type: 'fill',
								source: PRECINCT_SOURCE_ID,
								'source-layer': PRECINCT_SOURCE_LAYER,
								paint: {
									// Diverging ramp on yes_pct (0–100)
									'fill-color': [
										'interpolate',
										['linear'],
										['coalesce', ['get', 'yes_pct'], 0],
										0,
										'#b2182b',
										50,
										'#f7f7f7',
										100,
										'#2166ac'
									],
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
				} catch (err) {
					console.error('Failed to add precinct layers:', err);
				}
			}}
			style={mapLibreStyle}
		/>

		{#if activateCallout}
			<Callout
				header="Call Out box"
				copy="Sometimes we may want to have a prominent call out to add context or other interesting information as supplement to the graphic. This box could also be collapsible, showing only the header and then require a click on the container to expand this text you are reading."
				collapsible={false}
			/>
		{/if}

		{#if activateCta}
			<CallToActionBox
				header="Do you have a news tip to share with us?"
				copy="Share confidential news tips or sensitive information to us through a secure channel."
				linkUrl="https://forms.gle/wXsJNXe1iqezmBEV9"
				linkCopy="Send a tip"
			/>
		{/if}
	</section>

	<Credits
		credit="Testy McTestersen, CalMatters"
		source="California Department of Awesome"
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
</style>
