<!--
  @component
  Searchable dropdown for precincts in the selected county.
  Options are precinct IDs; the list is filtered by the selected county (passed in).
  Renders a combobox: filter input + list of precinct IDs.
-->

<script>
	const {
		precinctIds = [],
		selectedPrecinctId = null,
		onchange,
		label = 'Selected precinct',
		disabled = false,
		placeholder = 'Search precincts...'
	} = $props();

	let query = $state('');
	let open = $state(false);
	let highlightedIndex = $state(-1);
	let listId = 'precinct-list-0';
	let inputId = 'precinct-input-0';
	let wrapperEl = $state(null);

	/** Precinct IDs for the selected county, filtered by the search query. */
	const filteredPrecinctIds = $derived(
		query.trim() === ''
			? precinctIds
			: precinctIds.filter((precinctId) =>
					precinctId.toLowerCase().includes(query.trim().toLowerCase())
				)
	);

	/** Input shows search query while typing, or selected precinct ID when not searching. */
	const displayValue = $derived(query !== '' ? query : (selectedPrecinctId ?? ''));

	/** ID of the currently highlighted listbox option (for aria-activedescendant). */
	const highlightedOptionId = $derived(
		highlightedIndex >= 0 && filteredPrecinctIds[highlightedIndex]
			? `option-${filteredPrecinctIds[highlightedIndex]}`
			: undefined
	);

	function selectPrecinct(precinctId) {
		onchange(precinctId);
		query = '';
		open = false;
		highlightedIndex = -1;
	}

	function clear() {
		onchange(null);
		query = '';
		open = false;
		highlightedIndex = -1;
	}

	function handleKeydown(e) {
		if (!open) {
			if (e.key === 'ArrowDown' || e.key === 'Enter') {
				e.preventDefault();
				open = true;
				highlightedIndex = 0;
			}
			return;
		}
		if (e.key === 'Escape') {
			e.preventDefault();
			open = false;
			highlightedIndex = -1;
			return;
		}
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			highlightedIndex = Math.min(highlightedIndex + 1, filteredPrecinctIds.length);
			return;
		}
		if (e.key === 'ArrowUp') {
			e.preventDefault();
			highlightedIndex = Math.max(highlightedIndex - 1, -1);
			return;
		}
		if (e.key === 'Enter' && highlightedIndex === -1) {
			e.preventDefault();
			clear();
			return;
		}
		if (e.key === 'Enter' && highlightedIndex >= 0 && filteredPrecinctIds[highlightedIndex]) {
			e.preventDefault();
			selectPrecinct(filteredPrecinctIds[highlightedIndex]);
			return;
		}
	}

	$effect(() => {
		// Reset when precinctIds change (e.g. county changed)
		query = '';
		highlightedIndex = -1;
	});
</script>

<div class="precinct-select-container">
	<div class="label-and-control">
		<label for={inputId}>
			<span>{label}</span>
		</label>
		<div class="combobox-wrapper" bind:this={wrapperEl}>
		<input
			id={inputId}
			type="text"
			role="combobox"
			aria-expanded={open}
			aria-controls={listId}
			aria-autocomplete="list"
			aria-activedescendant={highlightedOptionId}
			value={displayValue}
			oninput={(e) => (query = e.currentTarget.value)}
			onfocus={() => (open = true)}
			onkeydown={handleKeydown}
			{disabled}
			{placeholder}
			class="combobox-input"
		/>
		{#if open}
			<ul
				id={listId}
				role="listbox"
				class="options-list"
			>
				<li
					role="option"
					id="option-clear"
					class="option"
					class:highlighted={highlightedIndex === -1 && open}
					aria-selected={highlightedIndex === -1}
					tabindex="-1"
					onclick={() => clear()}
					onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); clear(); } }}
					onmouseenter={() => (highlightedIndex = -1)}
				>
					—
				</li>
				{#each filteredPrecinctIds as precinctId, i}
					<li
						role="option"
						id="option-{precinctId}"
						class="option"
						class:highlighted={highlightedIndex === i}
						aria-selected={highlightedIndex === i}
						tabindex="-1"
						onclick={() => selectPrecinct(precinctId)}
						onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectPrecinct(precinctId); } }}
						onmouseenter={() => (highlightedIndex = i)}
					>
						{precinctId}
					</li>
				{/each}
				{#if filteredPrecinctIds.length === 0 && query.trim() !== ''}
					<li class="option option--empty">No matching precincts</li>
				{/if}
			</ul>
		{/if}
		</div>
	</div>
	<div class="legend-item">
		<div class="color-box" style="border-color: #212121;"></div>
		<p class="label">The selected precinct border</p>
	</div>
</div>

<svelte:window
	onclick={(e) => {
		if (open && wrapperEl && !wrapperEl.contains(e.target)) open = false;
	}}
/>

<style>
	.precinct-select-container {
		display: grid;
		grid-template-columns: 1fr 210px;
		margin: 16px 0;
		padding: 16px;
		background-color: var(--aqua_100);
		border-radius: 4px;
		font-family: var(--font-family);
	}

	@media screen and (max-width: 767px) {
		.precinct-select-container {
			padding: 12px;
		}
	}

	.label-and-control {
		display: flex;
		align-items: center;
		gap: 0;
	}

	label {
		font-weight: 700;
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
	}

	.combobox-wrapper {
		position: relative;
		margin-left: 10px;
	}

	.combobox-input {
		font-family: var(--font-family);
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
		padding: 6px 10px;
		border: 1px solid var(--gray_300);
		border-radius: 2px;
		background-color: var(--gray_000);
		width: 100%;
		min-width: 160px;
		box-sizing: border-box;
	}

	.combobox-input:focus-visible {
		outline: 2px solid var(--aqua_500);
		outline-offset: 2px;
	}

	.combobox-input::placeholder {
		color: var(--gray_400);
	}

	.options-list {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		margin: 4px 0 0 0;
		padding: 0;
		list-style: none;
		max-height: 240px;
		overflow-y: auto;
		background-color: var(--gray_000);
		border: 1px solid var(--gray_300);
		border-radius: 2px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		z-index: 10;
	}

	.option {
		padding: 8px 10px;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_600);
		cursor: pointer;
	}

	.option:hover,
	.option.highlighted {
		background-color: var(--aqua_100);
		color: var(--aqua_600);
	}

	.option--empty {
		cursor: default;
		color: var(--gray_400);
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
