<!--
 @component
 A radio button selector for racial demographic groups
 
 Allows users to select a racial group to highlight on the map.
 When a group is selected, matching precincts will have yellow borders.
-->
<script>
	const racialGroups = [
		'Hispanic Or Latino',
		'White',
		'Asian',
		'Black Or African American',
		'Multiracial'
	];

	let { selectedGroup = null, onSelect = () => {} } = $props();

	function handleChange(event) {
		const value = event.target.value;
		onSelect(value === 'none' ? null : value);
	}
</script>

<section class="selector">
	<p class="selector-title">Highlight Racial Group</p>
	<div class="radio-group">
		<label class="radio-option">
			<input
				type="radio"
				name="racial-group"
				value="none"
				checked={selectedGroup === null}
				onchange={handleChange}
			/>
			<span class="radio-label">None</span>
		</label>
		{#each racialGroups as group}
			<label class="radio-option">
				<input
					type="radio"
					name="racial-group"
					value={group}
					checked={selectedGroup === group}
					onchange={handleChange}
				/>
				<span class="radio-label">{group}</span>
			</label>
		{/each}
	</div>
</section>

<style lang="scss">
	.selector {
		margin: 16px 0;
		padding: 16px;
		background-color: var(--aqua_100);
		border-radius: 4px;
		font-family: var(--font-family);
		
		@media screen and (max-width: 767px) {
			padding: 12px;
		}
	}

	.selector-title {
		margin: 0 0 12px 0;
		font-weight: 700;
		font-size: var(--detail-size);
		line-height: var(--detail-height);
		color: var(--gray_600);
	}

	.radio-group {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		
		@media screen and (max-width: 767px) {
			gap: 12px;
		}
	}

	.radio-option {
		display: flex;
		align-items: center;
		gap: 8px;
		cursor: pointer;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_600);
		
		input[type="radio"] {
			margin: 0;
			cursor: pointer;
			width: 16px;
			height: 16px;
			accent-color: var(--aqua_500);
		}
		
		&:hover {
			color: var(--gray_600);
		}
	}

	.radio-label {
		user-select: none;
	}
</style>
