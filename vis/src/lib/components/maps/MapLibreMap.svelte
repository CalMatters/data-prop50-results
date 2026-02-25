<!--
 @component
 A wrapper around [MapLibre GL](https://maplibre.org).
 
Many props are simply passed right on through to [MapLibre](https://maplibre.org/maplibre-gl-js/docs/API/type-aliases/MapOptions/).
Over time, we'll add the ones we need.

* `center` - The center of the map, default: [-119.449444, 37.166111]
* `dragRotate` - Enable drag to rotate, default: false
* `interactive` - Enable panning/zooming for the map, default: true
* `load` - Function to be called after map loads, default: (map) => {}
* `style` - Style declaration object, default: {}
* `zoom` - Initial zoom level, default: 4.2

There are a few props that we added on, all of which are optional:

* `source` - The text for data and source attribution
* `sourceUrl` - A URL to link the source text to

The component will dispatch a `load` event at the end of `map.on('load')`,
passing it the [Map](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/)
object

-->

<script>
	import 'maplibre-gl/dist/maplibre-gl.css';
	import maplibregl from 'maplibre-gl';
	import { Protocol } from 'pmtiles';
	import { onMount } from 'svelte';

	const { Map } = maplibregl;
	let {
		center = [-119.449444, 37.166111],
		dragRotate = false,
		load = () => {},
		interactive = true,
		source = null,
		sourceUrl = null,
		style = {},
		zoom = 4.2,
		maxZoom = 13,
		minZoom = 0,
		maxBounds = [[-137.210999,24.723133],[-96.341858,46.344084]]
	} = $props();

	let container;
	let map;
	let mapHasLoaded = false;
	let protocol = new Protocol();

	onMount(() => {
		if (!container) {
			console.log('bouncing early because container is false-y');
			return;
		}

		maplibregl.addProtocol('pmtiles', protocol.tile);

		map = new Map({
			center,
			container,
			dragRotate,
			interactive,
			style,
			zoom,
			minZoom,
			maxZoom,
			maxBounds
		});

		function handleLoad() {
			mapHasLoaded = true;
			load(map);
		}

		function handleZoom() {
			const currentZoom = map.getZoom();
			zoom = currentZoom;
		}

		map.on('zoom', handleZoom);
		map.on('load', handleLoad);

		return () => {
			map.off('zoom', handleZoom);
			map.off('load', handleLoad);
			map.remove();
		};
	});
</script>

<div class="map-container">
	<div class="map" bind:this={container}>
		{#if map}
			<slot />
		{/if}
	</div>
	{#if source}
		<p class="chart-source">
			Source:
			{#if sourceUrl}
				<a href={sourceUrl}>{source}</a>
			{:else}
				{source}
			{/if}
		</p>
	{/if}
</div>

<style lang="scss">
	.map-container {
		height: 100%;
		position: relative;
		width: 100%;
		max-width: 1200px;
		margin: auto;
	}

	.map {
		height: 100%;
		margin-bottom: 1rem;
		min-height: var(--min-height, 600px);
		width: 100%;
	}
</style>
