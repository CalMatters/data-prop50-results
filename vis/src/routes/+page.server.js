/** @type {import('./$types').PageLoad} */
export function load({ url }) {
  const county = url.searchParams.get("county"); // returns null if not found

  return {
    county,
  };
}
