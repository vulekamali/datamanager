import filterKeywords from "./filterKeywords.js";
import filterFunctiongroup1s from "./filterFunctiongroup1s.js";
import filterDepartments from "./filterDepartments.js";

export default function filterResults(filtersObject, rawItems) {
  const filtersKeys = Object.keys(filtersObject);

  return filtersKeys.reduce((results, key) => {
    const value = filtersObject[key];

    if (key === "keywords" && value.length > 2) {
      return filterKeywords(value, results);
    }

    if (key === "functiongroup1" && value !== "all") {
      return filterFunctiongroup1s(results, value);
    }

    if (key === "department" && value !== "all") {
      return filterDepartments(results, value);
    }

    return results;
  }, rawItems);
}
