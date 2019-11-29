export function formatCurrency(decimalString) {
  if (decimalString == null)
    return null;
  return "R " + Math.round(parseFloat(decimalString)).toLocaleString();
}

export const statusOrder = [
  "Project Initiation",
  "Pre - Feasibility",
  "Feasibility",
  "Tender",
  "Design",
  "Site Handed - Over to Contractor",
  "Construction 1% - 25%",
  "Construction 26% - 50%",
  "Construction 51% - 75%",
  "Construction 76% - 99%",
  "Practical Completion (100%)",
  "Final Completion",
  "On Hold",
  "Terminated",
  "Other - Compensation of Employees",
  "Other - Packaged Ongoing Project",
];

/**
 * Returns a new array of the elements of unsortedArray, ordered according to
 * the order of strings in orderArray.
 *
 * Returns an array that contains one object for each of the union
 * of unique strings in orderArray and sortKey values in unsortedArray objects.
 *
 * Strings in orderArray that don't occur in unsortedArray will result in
 * objects with only they field sortKey with that string.
 *
 * Objects in unsortedArray whose sortKey does not exist in orderArray
 * will appear in unsortedArray order at the end of the returned array.
 */
export function sortByOrderArray(orderArray, sortKey, unsortedArray) {
  // Initialise map
  const map = new Map(orderArray.map(function(key) {
    const defaultElement = {};
    defaultElement[sortKey] = key;
    return [key, defaultElement];
  }));

  // Add unsorted elements
  unsortedArray.forEach(el => map.set(el[sortKey], el));

  // Output array
  const sortedArray = [];
  map.forEach(val => sortedArray.push(val));
  return sortedArray;
}

// Ordered map of options. Keys are the query string values to pass to the API.
export const sortOptions = new Map([
  ["total_project_cost", "Total Estimated Project Cost (Ascending)"],
  ["-total_project_cost", "Total Estimated Project Cost (Descending)"],
  ["status_order", "Status (Ascending)"],
  ["-status_order", "Status (Descending)"],
  ["estimated_completion_date", "Estimated Project Completion Date (Ascending)"],
  ["-estimated_completion_date", "Estimated Project Completion Date (Ascending)"],
]);

export function coordsAvailable(lat, lon) {
  // Don't try and parse null
  // Parse because "0" is true
  return (lat && parseInt(lat)) && (lon && parseInt(lat));
}
