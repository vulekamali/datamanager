
export default function normaliseRawValues(rawValues) {
  const items = rawValues.reduce(
    (results, val) => {
      return {
        ...results,
        [val.name]: [val.total_budget],
      };
    },
    {},
  );

  const files = Object.keys(rawFiles).reduce(
    (results, key) => {
      const object = rawFiles[key].formats.reduce(
        (innerResults, val) => {
          return {
            ...innerResults,
            [`${key} (${val.format.replace(/^xls.+/i, 'Excel')})`]: val.url,
          };
        },
        {},
      );

      return {
        ...results,
        ...object,
      };
    },
    {},
  );

  return items;
}
