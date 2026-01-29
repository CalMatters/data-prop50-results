# Svelte Graphics Template
This template is used primarily for embedding or injecting graphics onto the CalMatters website. Additional work will need to be done to allow for use with The Markup CMS as well.

The template is currently configured for Svelte 5 and with use on Netlify. This repo can be used to host graphics or data routes (Netlify Functions).

The main route `/` contains an example structure for graphics that can be adapted based on need. The `/components` route provides examples of the kinds of components we currently offer in the updated template. It is advised to delete the `/components` route before pushing to production. 

Documentation for each component can be found inside the component file. `/components` also contains additional documentation. Documentation on Svelte [can be found here](https://svelte.dev/docs/svelte/overview).

## Creating a project

1. Create a new repo on Github using this repo as the template
2. Clone the new repo locally `git clone url-of-new-repo`
3. Go to the cloned directory and run `npm i` to install dependencies located in `package.json`

## Developing

Once you've created a project and installed dependencies, start a development server:

```bash
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

The project will load on `localhost:3000`. If that is already spoken for, it will iterate from there to `localhost:3001` and so forth.

If you are interested in using this template solely for managing a data endpoint or wish to have one incorporated for a graphic living in this repo, see `data/data.mjs` on how to link a csv file and convert it into a json file. `functions` contains the file(s) that would be used to create endpoints on Netlify using their Functions. 

If you wish to add a Github action to the repo, look at `.github/workflows/example.yml` for a basic example of an action that is manually triggered or set to run at an interval (that is commented out and you can [reference this resource](https://crontab.guru/) to configure timing of actions).

## Building

To create a production version of your app locally:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

CalMatters visual guide is installed on the project template and located in `src/styles/guide.scss`. There are class configurations for text sizing and variables for all the colors we currently have in the visual guide. We also load the CMS stylesheet into the project for enhanced visual compatability when embedding.  

## Deploying

Generally, our approach to deploying is to connect the project repo to a Netlify site. The Netlify site will rebuild every time a new version is pushed to the connected Github repo. We generally name the Netlify site `calmatters-name_of_repo` but there may be reasons to do otherwise. 

You can configure the Netlify site to be password protected or to allow for deploy previews based on different branches of the repo, within the Netlify site options.

Read more [documentation on how we use Netlify](https://calmatters.atlassian.net/wiki/spaces/DATA/pages/888373284/Using+Netlify) in Confluence.

## Embedding

Generally, graphics using this template are embedded into the CalMatters CMS using the `pym.js` block. Pym.js is loaded into the template by default and requires no further configuration for basic use. The `pym.js` block can be configured for "full width" or aligned to either site depending on need. 

Note that by default, the width of a project using this template is set to a max width of 780px, which is the width of most article pages on the CMS. If you plan on embedding a graphic at full width, you will need to adjust the max width located in CSS of the `+page.svelte` file. 

## Future

1. Integrate The Markup visual style guide and injection approach into the template. Allow for one graphics to be developed for both CMS solutions with minimal adjustments required.

2. Explore incorporating open source visual libraries such as LayerCake for charts and MapLibre for mapping, along with accompanying components.

3. Only the most used components from the old version of the template have been ported to this one. Explore whether we want to incorporate any additional components or features, such as the Timeline or other UI components not used regularly.

