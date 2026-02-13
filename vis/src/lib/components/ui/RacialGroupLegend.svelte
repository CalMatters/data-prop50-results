<!--
 @component
 A legend for racial group colors with saturation variance explanation

 Shows each racial group with its color and explains how saturation
 varies based on the selected metric (yes_pct or vote_shift).
-->
<script>
	import { RACIAL_GROUP_COLORS } from '$lib/racial-group-colors.js';

	let {
		saturationMetric = 'yes_pct',
		onSaturationMetricChange = () => {}
	} = $props();

	const SATURATION_OPTIONS = [
		{ value: 'yes_pct', label: 'Prop 50 yes %' },
		{ value: 'vote_shift', label: 'Vote shift vs Harris 2024' }
	];

	const racialGroups = [
		{ label: 'Hispanic Or Latino', color: RACIAL_GROUP_COLORS['Hispanic Or Latino'] },
		{ label: 'White', color: RACIAL_GROUP_COLORS['White'] },
		{ label: 'Asian', color: RACIAL_GROUP_COLORS['Asian'] },
		{ label: 'Black Or African American', color: RACIAL_GROUP_COLORS['Black Or African American'] },
		{ label: 'Multiracial', color: RACIAL_GROUP_COLORS['Multiracial'] }
	];

	// Colors for saturation gradient examples (matching the interpolation in +page.svelte)
	const saturationExamples = {
		'White': { light: '#E8F2FA', medium: '#9BC0E0', dark: RACIAL_GROUP_COLORS['White'] },
		'Multiracial': { light: '#F0E8F7', medium: '#C9A5E1', dark: RACIAL_GROUP_COLORS['Multiracial'] },
		'Hispanic Or Latino': { light: '#FBF0E5', medium: '#F2B872', dark: RACIAL_GROUP_COLORS['Hispanic Or Latino'] },
		'Black Or African American': { light: '#E8F5E3', medium: '#8DCC6F', dark: RACIAL_GROUP_COLORS['Black Or African American'] },
		'Asian': { light: '#FAE8E6', medium: '#E18A7F', dark: RACIAL_GROUP_COLORS['Asian'] }
	};
</script>

<section class="legend">
	<p class="legend-title">Racial Groups</p>
	<div class="legend-items">
		{#each racialGroups as group}
			<div class="legend-item">
				<div class="color-box" style="background-color: {group.color}"></div>
				<p class="label">{group.label}</p>
			</div>
		{/each}
	</div>
	
	<div class="saturation-note">
		<p class="note-title">
			Color Saturation:
			<select
				value={saturationMetric}
				onchange={(e) => onSaturationMetricChange(e.currentTarget.value)}
				aria-label="Saturation metric"
			>
				{#each SATURATION_OPTIONS as opt}
					<option value={opt.value}>{opt.label}</option>
				{/each}
			</select>
		</p>
		<p class="note-text">
			{#if saturationMetric === 'yes_pct'}
				The saturation of each color varies based on the percentage of "yes" votes in that precinct.
				Darker, more saturated colors indicate higher percentages of "yes" votes, while lighter colors
				indicate lower percentages.
			{:else}
				The saturation of each color varies based on the shift in support from Harris (2024) to Prop 50 (2025).
				Darker colors indicate more shift toward Prop 50; lighter colors indicate less shift or shift away.
			{/if}
		</p>
		<div class="saturation-example">
			<div class="gradient-bar">
				<div class="gradient-fill" style="background: linear-gradient(to right, #FFFFFF, #333333)"></div>
				<div
					class="midpoint-indicator"
					title={saturationMetric === 'yes_pct' ? '50% - Yes wins above this line' : '0% - No shift'}
				></div>
			</div>
			<div class="gradient-labels">
				{#if saturationMetric === 'yes_pct'}
					<span>Yes losing</span>
					<span class="midpoint-label">50%</span>
					<span>Yes winning</span>
				{:else}
					<span>−15%</span>
					<span class="midpoint-label">0%</span>
					<span>+15%</span>
				{/if}
			</div>
		</div>
	</div>
</section>

<style lang="scss">
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

	.saturation-note .note-title select {
		margin-left: 8px;
		font-family: var(--font-family);
		font-size: var(--detail-size);
		font-weight: 600;
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
