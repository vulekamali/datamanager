const recursiveReduce = (result, { name, items, amount }) => {
  return {
    ...result,
    [name]: amount || items.reduce(recursiveReduce, {}),
  };
};


const normaliseAdjusted = (rawItems, rotated) => {
  const itemsData = rawItems.reduce(recursiveReduce, {});

  const addEmptyBars = (amount) => {
    const result = {};

    for (let i = 0; i < amount; i++) {
      result[`empty: ${i}`] = 0;
    }

    return result;
  };

  const data = {
    ...itemsData,
    ...(rotated ? addEmptyBars(9 - Object.keys(itemsData).length) : {}),
  };

  return { data };
};


export default normaliseAdjusted;
