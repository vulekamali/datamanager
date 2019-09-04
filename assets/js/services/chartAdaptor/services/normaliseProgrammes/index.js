const normaliseProgrammes = (rawItems) => {
  const data = rawItems.reduce(
    (results, { name, total_budget: value }) => {
      return {
        ...results,
        [name]: value,
      };
    },
    {},
  );

  return { data };
};


export default normaliseProgrammes;
