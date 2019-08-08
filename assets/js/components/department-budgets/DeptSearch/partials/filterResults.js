import filterKeywords from './filterKeywords.js';
import filterGroups from './filterGroups.js';


export default function filterResults(filtersObject, rawItems) {
  const filtersKeys = Object.keys(filtersObject);


  return filtersKeys.reduce(
    (results, key) => {
      const value = filtersObject[key];

      if (key === 'keywords' && value.length > 2) {
        return filterKeywords(value, results);
      }

      if (key === 'sphere' && value === 'national') {
        return filterGroups(results, 'south-africa');
      }

      if (key === 'sphere' && value === 'provincial') {
        return filterGroups(results, 'south-africa', true);
      }

      if (key === 'province' && value !== 'all') {
        return filterGroups(results, value);
      }

      return results.map((item) => {
        const newOrderDept = item.departments.sort(
          (a, b) => {
            return a.name.localeCompare(b.name);
          },
        );

        return {
          ...item,
          departments: newOrderDept,
        };
      });
    },
    rawItems,
  );
}
