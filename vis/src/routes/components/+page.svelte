<script>
	// Svelte Components
	import Credits from "$lib/components/ui/Credits.svelte";
    import Header from "$lib/components/ui/Header.svelte";
	import Callout from "$lib/components/Callout.svelte";
	import CallToActionBox from "$lib/components/CallToActionBox.svelte";
	import AlertBox from "$lib/components/ui/alert/AlertBox.svelte";
	import Legend from "$lib/components/ui/Legend.svelte";
	import Button from "$lib/components/ui/Button.svelte";
	import AddressLookup from "$lib/components/AddressLookup.svelte";
	import Search from "$lib/components/Search.svelte";
	import MapboxMap from "$lib/components/maps/MapboxMap.svelte";

    // for address lookup dispatch event
    let addressDispatch = $state(false);

    // for button dispatch event
    let buttonDispatch = $state( false );

    // for search dispatch event
    let searchDispatch = $state(false);


    // legend component example
    const legendData = [
        {
            label: "Cold",
            color: "#05B9D7"
        },
        {
            label: "Colder",
            color: "#0A819F"
        },
        {
            label: "Frozen",
            color: "#075E73"
        },
    ]

</script>

<main class="graphic">
    <h1>List of Components</h1>
    <p>Each component has detailed documentation on how to use it in the component file. Feel free to delete this route before publishing something live.</p>

    <div>
        <div class="component-header">
            <p class="component-name">Address Lookup Component</p>
            <p>Add an address lookup to your interactive for lookup tools. Uses Google Places API administered by Google Cloud. <a href="https://docs.google.com/document/d/1rzT6W9TWnmEpToIhONJNzvwjLS1Cf1rFDS1x6YBScOw/edit?tab=t.0">Will work on localhost:3000, 3001 and 3002, but follow rules here to configure for production.</a> By default, geofenced to California, but there may be use cases to remove, such as Jeremia's fire map overlay tool. Dispatches address and lat/lng to parent.</p>
        </div>
        
        <AddressLookup 
            dispatchEvent={ (e) => { addressDispatch = e } }
        />

        {#if addressDispatch }
            <p>Dispatch event:</p>
            <p>{ addressDispatch.formatted } at { addressDispatch.lat }, { addressDispatch.lng }</p>
        {/if}

    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Alert Component</p>
            <p>A component for alerting the user about the graphic or an interaction. Has a variety of states depending on need.</p>
        </div>
        <AlertBox 
            type="info"
            text="Did you know I exist now? I feel so <strong>ALIVE</strong>!"
        />
        <AlertBox 
            type="success"
            text="You did it! Congrats :)"
        />
        <AlertBox 
            type="warning"
            text="We couldn't locate what you were looking for."
        />
        <AlertBox 
            type="strongWarning"
            text="Umm, you should probably not do this."
        />
        <AlertBox 
            type="fail"
            text="War were declared."
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Button Component</p>
            <p>A button that can send a dispatch event back to the parent. In the Button component, you can configure the onclick/onkeyup event listeners to send something back to the parent using the `dispatchLabel` property. In the parent, you can take what is sent and call a function to do something with it.</p>
        </div>
        
        <Button
            size="compact"
            dispatchLabel={ ( e ) => { buttonDispatch = true } }
        >Press Me</Button> 

        {#if buttonDispatch }
            <p>Dispatch from Button component received.</p>
        {/if}

    </div>
    
    <div>
        <div class="component-header">
            <p class="component-name">Call Out Box Component</p>
            <p>A styled call out box. Can use for methodology or other use cases where you want to break user flow to highlight something.</p>
        </div>
        <Callout 
            header="Call Out Box"
            copy="Sometimes we may want to have a prominent call out to add context or other interesting information as supplement to the graphic. This box could also be collapsible, showing only the header and then require a click on the container to expand this text you are reading."
            collapsible={ false }
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">CTA Box Component</p>
            <p>A styled element to send people somewhere to take action on something.</p>
        </div>
        <CallToActionBox 
            header="Do you have a news tip to share with us?"
            copy="Share confidential news tips or sensitive information to us through a secure channel."
            linkUrl="https://forms.gle/wXsJNXe1iqezmBEV9"
            linkCopy="Send a tip"
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Credits Component</p>
            <p>A mandatory component for the bottom of the graphic giving credit and notes about the graphic.</p>
        </div>
        <Credits
            credit="Testy McTestersen, CalMatters"
            source="California Department of Awesome"
            note="No pixels were harmed in the creation of this example route."
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Header Component</p>
            <p>Required component for custom graphics.</p>
        </div>
        <Header
            title="This is the headline for the graphic"
            copy="If there is any supporting context or other information that's important to know before digesting the graphic, this is where it goes."
            size="inline"
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Legend Component</p>
            <p>A legend to accompany a map or graphic. Can handle a filled box or outlines for map perimeters and the like.</p>
        </div>
        <Legend
            data={ legendData }
            label="How cold is it?"
        />
        <Legend
            data={ legendData }
            label="How cold is it?"
            outlineOnly={ true }
        />
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">MapBox Component</p>
            <p>Create a simple MapBox instance, which can be further refined and customized inside the component file.</p>
        </div>
        <MapboxMap />
        
    </div>

    <div>
        <div class="component-header">
            <p class="component-name">Search Component</p>
            <p>A search input that dispatches the value of the search back to the parent.</p>
        </div>
        <Search 
            placeholder="What is your greatest fear?"
            searchDispatch={ (e) => { searchDispatch = e } }
        />

        {#if searchDispatch }
            <p>Dispatch event:</p>
            <p>Do not fear { searchDispatch }, for you are as strong as the stars you are made from.</p>
        {/if}

    </div>
    
</main>

<div style="height:40px;"></div>


<style lang="scss">
    main {
        max-width: 780px;
        margin: 0 auto;

        .component-header {
            margin: 48px 0 32px 0;

            p {
                margin: 0;
            }
        }

        .component-name {
            display: inline-block;
            padding: 4px 8px;
            background-color: var( --gray_600 );
            color: #fff;
        }
    }
</style>