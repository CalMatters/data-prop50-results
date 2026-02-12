<!--
 @component
 A legend for election results with blue-red diverging gradient
 
 Shows a gradient from red (no votes) to blue (yes votes) with
 a midpoint indicator at 50%.
-->
<script>
	// Color values matching CSS variables from guide.scss
	const RED_COLOR = '#D35F4F'; // --red_500
	const BLUE_COLOR = '#5B92CE'; // --blue_500
	const MIDPOINT_COLOR = '#EEEEEE'; // --gray_100
</script>

<section class="legend">
	<p class="legend-title">Election Results</p>
	
	<div class="gradient-section">
		<div class="gradient-bar">
			<div class="gradient-fill" style="background: linear-gradient(to right, {RED_COLOR}, {MIDPOINT_COLOR} 50%, {BLUE_COLOR})"></div>
			<div class="midpoint-indicator" title="50% - Yes wins above this line"></div>
		</div>
		<div class="gradient-labels">
			<span>No</span>
			<span class="midpoint-label">50%</span>
			<span>Yes</span>
		</div>
	</div>
	
	<p class="note-text">
		Colors represent the percentage of "yes" votes in each precinct. 
		Blue indicates higher support for Prop 50, while red indicates lower support.
	</p>
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

	.gradient-section {
		margin-bottom: 12px;
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

	.note-text {
		margin: 0;
		font-size: var(--footnote-size);
		line-height: var(--footnote-height);
		color: var(--gray_400);
	}
</style>
