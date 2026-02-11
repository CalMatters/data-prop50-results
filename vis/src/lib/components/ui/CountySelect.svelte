<!--
 @component
 A dropdown menu with all California counties
 
-->

<script>
	const counties = [
		'Alameda',
		'Alpine',
		'Amador',
		'Butte',
		'Calaveras',
		'Colusa',
		'Contra Costa',
		'Del Norte',
		'El Dorado',
		'Fresno',
		'Glenn',
		'Humboldt',
		'Imperial',
		'Inyo',
		'Kern',
		'Kings',
		'Lake',
		'Lassen',
		'Los Angeles',
		'Madera',
		'Marin',
		'Mariposa',
		'Mendocino',
		'Merced',
		'Modoc',
		'Mono',
		'Monterey',
		'Napa',
		'Nevada',
		'Orange',
		'Placer',
		'Plumas',
		'Riverside',
		'Sacramento',
		'San Benito',
		'San Bernardino',
		'San Diego',
		'San Francisco',
		'San Joaquin',
		'San Luis Obispo',
		'San Mateo',
		'Santa Barbara',
		'Santa Clara',
		'Santa Cruz',
		'Shasta',
		'Sierra',
		'Siskiyou',
		'Solano',
		'Sonoma',
		'Stanislaus',
		'Sutter',
		'Tehama',
		'Trinity',
		'Tulare',
		'Tuolumne',
		'Ventura',
		'Yolo',
		'Yuba'
	];

	const { initialValue = undefined, label, onchange } = $props();

	// will be the initial value of the select element
	let selected = $state(initialValue);

	$effect(() => {
		onchange(selected);
	});
</script>

<div class="county-select-container">
	<label>
		<span>{label}</span>
		<select bind:value={selected}>
			<option>--</option>
			{#each counties as county}
				<option value={county.toLowerCase()}>
					{county}
				</option>
			{/each}
		</select>
	</label>
	<div class="legend-item">
		<div class="color-box" style="border-color: #212121;"></div>
		<p class="label">The selected county border</p>
	</div>
</div>

<style>
	.county-select-container {
		display: grid;
		grid-template-columns: 1fr 210px;
		margin: 16px 0;
		padding: 16px;
		background-color: var(--aqua_100);
		border-radius: 4px;
		font-family: var(--font-family);

		@media screen and (max-width: 767px) {
			padding: 12px;
		}
	}

	label {
		font-weight: 700;
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
	}

	select {
		margin-left: 10px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.color-box {
		border-style: solid;
		border-width: 2px;
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
</style>
