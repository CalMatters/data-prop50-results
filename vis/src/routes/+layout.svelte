<script>
	import { dev } from '$app/environment';

	const embed = true;
	const darkMode = false;

	loadCSS();

	async function loadCSS() {
		if (embed) {
			await import('../styles/cms.css');
			console.log('Loaded CSS files for embedding');
		} else if (!embed && dev) {
			await import('../styles/cms.css');
			console.log('Loaded CSS files for injection');
		}

		await import('../styles/guide.scss');
	}
</script>

<slot />

<style>
	main {
		padding-bottom: 1rem;
	}
</style>
