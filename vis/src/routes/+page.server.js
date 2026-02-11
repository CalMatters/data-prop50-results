/** @type {import('./$types').PageLoad} */
export function load({ url }) {
  const county = url.searchParams.get("county", undefined);

  return {
    county,
  };
}
