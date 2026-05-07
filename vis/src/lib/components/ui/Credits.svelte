<!--
 @component
 A styled credit section
 
 Generates a styled area at the bottom of the graphic with credit, source, notation text, and an optional embed code 

 1. `credit` the people who helped create the graphic. `REQUIRED`
 2. `source` the source for any data used in the graphic; html ok. `REQUIRED`
 3. `note` if there is additional context or methodology required to source or explain the graphic; html ok. OPTIONAL
 4. `allowEmbed` boolean, shows embed option. DEFAULT is true

Component generates a simple container to structure how we inform readers who made the graphic, where we got the data used in the graphic and any other context required to understand how we used the data or the nature of the data itself. 

-->

<script>
	import EmbedCode from '$lib/components/ui/EmbedCode.svelte';
	//component properties
	let { credit = '', source = '', note = '', allowEmbed = true } = $props();

	let isEmbedOpen = $state(false);
</script>

<section class="credits">
	{#if isEmbedOpen}
		<div class="embed-container">
			<EmbedCode onclose={() => (isEmbedOpen = false)} />
		</div>
	{/if}

	<ul>
		{#if note !== ''}
			<li class="footnote"><strong>Note:</strong> {@html note}</li>
		{/if}

		{#if source !== ''}
			<li class="footnote"><strong>Source:</strong> {@html source}</li>
		{/if}

		{#if credit !== ''}
			<li class="footnote"><strong>Credits:</strong> {@html credit}</li>
		{/if}

		{#if allowEmbed}
			<li class="footnote">
				<button class="embed-button" onclick={() => (isEmbedOpen = true)}>
					Embed this graphic
				</button>
			</li>
		{/if}
	</ul>
</section>

<style lang="scss">
	.credits {
		display: flex;
		flex-direction: column;
		padding-top: 12px;
		margin-top: 12px;
		border-top: 1px solid #ccc;
		position: relative;

		ul {
			list-style-type: none;
			padding: 0;
			margin: 0;

			li {
				margin: 0 0 4px 0;
			}
		}

		.embed-container {
			bottom: 0;
			position: absolute;
			min-width: 300px;
			max-width: 500px;
			width: 100%;

			@media screen and (min-width: 650px) {
				bottom: 0.5em;
				left: 1em;
			}
		}

		button.embed-button {
			background-color: transparent;
			color: var(--aqua_400);
			font-family: var(--font-family);
			font-size: var(--footnote-size);
			font-weight: 400;
			line-height: var(--footnote-height);
			margin-bottom: 0;
			padding: 0;
			text-decoration: underline;
		}
	}
</style>
