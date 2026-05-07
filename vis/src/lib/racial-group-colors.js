/**
 * Color mappings for racial demographic groups
 * Colors are from the CalMatters design system (guide.scss)
 */

/**
 * Normalizes racial group names by collapsing "Multiracial (X plurality)" variants
 * to a single "Multiracial" category.
 *
 * @param {string|null|undefined} group - The racial group name
 * @returns {string|null} - Normalized group name or null
 */
export function normalizeRacialGroup(group) {
	if (!group || group === null || group === undefined || String(group).toLowerCase() === 'nan') {
		return null;
	}

	const groupStr = String(group);
	if (groupStr.startsWith('Multiracial')) {
		return 'Multiracial';
	}

	return groupStr;
}

/**
 * Color mapping for normalized racial groups.
 * Colors are selected from the CalMatters secondary palette.
 * MapLibre need to be static so we aren't loading the CSS variables from the guide.scss file.
 *
 * @type {Record<string, string>}
 */
export const RACIAL_GROUP_COLORS = {
	White: '#5B92CE', // blue_500 - distinct blue
	Multiracial: '#B18DCC', // violet_500 - distinct purple
	'Hispanic Or Latino': '#E58F40', // orange_500 - warm orange
	'Black Or African American': '#5A9F3A', // green_500 - distinct green
	Asian: '#D35F4F', // red_500 - distinct red
	null: '#CCCCCC', // gray_300 - neutral grey for null/nan values
	undefined: '#CCCCCC' // gray_300 - neutral grey for undefined values
};

/**
 * Gets the color for a racial group, handling normalization.
 *
 * @param {string|null|undefined} group - The racial group name
 * @returns {string} - Hex color code
 */
export function getRacialGroupColor(group) {
	const normalized = normalizeRacialGroup(group);
	return RACIAL_GROUP_COLORS[normalized] || RACIAL_GROUP_COLORS[null];
}
