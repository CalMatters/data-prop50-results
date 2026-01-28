/*
* This file runs a script that will pull a csv from Google Sheets or another source and transform it into a json file. Additional modifications can be made before exporting a json file based on your needs.
* Use command "npm run data:sheets" to execute
*/

import fs from 'fs/promises'; // used to write to disk
import Papa from 'papaparse'; // transforms csv into json

/** 
/* Location of csv (probably Google Sheet) that we're injecting and transforming
/* @type {string}  
*/
const sheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vR5oroFFG-MW9lKWeJEqGLn1IrZkCcUc9sGQVIePCVqnB7aq4K58RKUdcOkfsFx3aC4kIwrrUsXdreC/pub?gid=0&single=true&output=csv';

/** 
/* The transformed data for export
/* @type {Array}  
*/
let csvData = [];

/**
 * Fetches csv and transforms into json
 * @param {string} url location of the csv file
 * @return {Array} formatted spreadsheet data in json form
 */
async function loadDataSource( url ){
    let data = [];

    try {
        const response = await fetch( url );
        const csvData = await response.text();
        Papa.parse( csvData, {
            header: true, 
            complete: ( results ) => {
                data = results.data;
            },
        });
        return data;
    }
    catch( e ){
        console.log( e );
    }

}

// ------------------------------------------------------------------ //

// fetch and transform data
csvData = await loadDataSource( sheet );

// write to data directory
await fs.writeFile( './data/data.json', JSON.stringify( csvData, null, 2 ) );
