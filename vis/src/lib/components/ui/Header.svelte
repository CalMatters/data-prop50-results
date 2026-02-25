<!--
 @component
 A styled header
 
 Generates a styled header for the graphic.

 1. `title` the headline. `REQUIRED`
 2. `copy` any supporting copy contextualizing the graphic. `REQUIRED`
 3. `size` inline (smaller) or section (larger) `REQUIRED`

Component generates a simple container with the `title` as an `h3` element and `copy` as a `p` tag with html support.

-->
<script>
    // component properties
    let {
        title = null,
        copy = null,
        size = null
    } = $props();

</script>

<section>

    {#if size == 'inline' }
        <h4>{ title }</h4>
        <p>{@html copy }</p>
    {:else if size == 'section' }
        <h3>{ title }</h3>
        <p class="large">{@html copy }</p>
    {/if}
    
    

</section>

<style lang="scss">

section {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 4px solid #0A819F;
}

h3, h4 {
    margin: 0;
    padding-bottom: 8px;
    font-weight: 700;
}

</style>