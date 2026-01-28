<!--
 @component
 A component for copying a PymJS embed code from a <textarea> 

 1. `graphicUrl` the public URL of the graphic/interactive, usually a Netlify URL. `REQUIRED`
 2. `onclose` a callback function to be invoked when the close button is clicked; required for button to show up


-->

<script>
	let { graphicUrl = `https://calmatters-svelte-template-new.netlify.app/`, onclose = null } =
		$props();
	let value =
		`<script type="text/javascript" src="https://pym.nprapps.org/pym.v1.min.js"><` +
		`/script>
<div id="pym-cm-embed"></div>
<` +
		`script>
  new pym.Parent('pym-cm-embed', '${graphicUrl}', {});
</` +
		`script>`;

	let isCopied = $state(false);

	async function copy() {
		if (!navigator.clipboard) return;

		await navigator.clipboard.writeText(value);
		isCopied = true;

		setTimeout(() => {
			isCopied = false;
		}, 2200);
	}
</script>

<div class="embed">
	{#if onclose}
		<div class="close-button-container">
      <div></div>
			<button class="close-button" onclick={onclose}>Close</button>
		</div>
	{/if}
	<textarea {value} rows={7} readonly={true}></textarea>
	<button onclick={copy}>
		{#if isCopied}
			Copied!
		{:else}
			Copy embed code
		{/if}
	</button>
</div>

<style>
	.embed {
		background-color: white;
		border: 1px solid #cccccc;
		padding: 8px;
		box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
	}
	.close-button-container {
    display: grid;
    grid-template-columns: 1fr 40px;
    margin-bottom: 4px;
	}
	.close-button {
		background-color: transparent;
		color: #212121;
		display: inline-block;
    margin: 0;
    padding: 0;
		text-align: right;
	}
	.close-button:hover,
	.close-button:focus {
		background-color: transparent;
	}
	textarea {
		font-family: monospace;
		font-size: 12px;
		margin-bottom: 8px;
		resize: none;
		background: #EEEEEE;
	}
	button {
		margin-bottom: 0 !important;
	}
</style>
