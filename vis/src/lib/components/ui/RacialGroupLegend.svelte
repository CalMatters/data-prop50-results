<!--
 @component
 A legend for racial group colors with saturation variance explanation
 
 Shows each racial group with its color and explains how saturation
 varies based on yes_pct (vote percentage).
-->
<script>
	import { RACIAL_GROUP_COLORS } from '$lib/racial-group-colors.js';

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
		<p class="note-title">Color Saturation</p>
		<p class="note-text">
			The saturation of each color varies based on the percentage of "yes" votes in that precinct. 
			Darker, more saturated colors indicate higher percentages of "yes" votes, while lighter colors 
			indicate lower percentages.
		</p>
		<div class="saturation-example">
			<div class="gradient-bar">
				<div class="gradient-fill" style="background: linear-gradient(to right, {saturationExamples['Hispanic Or Latino'].light}, {saturationExamples['Hispanic Or Latino'].dark})"></div>
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
