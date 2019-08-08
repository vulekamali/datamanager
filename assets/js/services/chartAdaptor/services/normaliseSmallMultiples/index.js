const recursiveReduce = (result, { name, items, total_budget: value }) => {
  return {
    ...result,
    [name]: value || items.reduce(recursiveReduce, {}),
  };
};


const normaliseSmallMultiples = (rawItems) => {
  const data = rawItems.reduce(recursiveReduce, {});
  return { data };
};


export default normaliseSmallMultiples;
