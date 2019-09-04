const normaliseExpenditure = (data) => {
  const {
    nominal: nominalRaw,
    real: realRaw,
  } = data;

  const createObject = (result, { financial_year: year, amount: value }) => ({
    ...result,
    [year]: value,
  });

  const nominal = nominalRaw.reduce(createObject, {});
  const real = realRaw.reduce(createObject, {});

  return { nominal, real };
};


export default normaliseExpenditure;
