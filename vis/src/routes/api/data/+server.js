import { json } from '@sveltejs/kit';
import { readFileSync } from 'fs';
import { resolve } from 'path';

/**
 * Retrieve json from requested route. Grab local version generated from data.mjs if inside dev environment. 
 * @return {Array|Object} the response from the route fetched
 */
export async function GET() {
    // check to see if we're inside the dev environment. Then resolve which path to retrieve. First path is local; second path external source, probably a Netlify function route of a json created by data.mjs.
    const dev = __SVELTEKIT_DEV__ ;
    const whichPath = dev ? 'data/data.json' : 'https://calmatters-trump-lawsuit-tracker.netlify.app/.netlify/functions/data';
    const filePath = resolve( whichPath );

    try {
        console.log( `Attempting to load json data from: ${ filePath }` );
        let fileContents;

        if ( dev ){
            fileContents = JSON.parse( readFileSync( filePath, 'utf-8' ) );
        }
        else {
            const response = await fetch( whichPath );

            if ( response.ok ) {
                fileContents = await response.json();
            }
            else {
                throw new Error(`Failed to fetch JSON: ${ response.statusText }`);
            }

        }

        console.log( `Successfully fetched ${ filePath }.` )

        return json( fileContents );
    }
    catch( error ){
        console.error('Error loading JSON data:', error);
        return json({ error: 'Internal server error' }, { status: 500 });
    }
}