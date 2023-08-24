const convertPhaseIntoNumber = (phaseString) => {
  switch (phaseString) {
    case 'Main appropriation': return 1;
    case 'Adjusted appropriation': return 2;
    case 'Final Appropriation': return 3;
    case 'Audit Outcome': return 4;
    default: throw (new Error(`Unknown phase: ${phaseString}`));
  }
};


const convertYearIntoNumber = (yearString) => {
  return parseInt(yearString.match(/^\d+/), 10);
};


const forcePhaseOrder = (itemsArray) => {
  return itemsArray.sort(
    (a, b) => convertPhaseIntoNumber(a.phase) - convertPhaseIntoNumber(b.phase),
  );
};


const forceYearOrder = (itemsObject) => {
  const years = Object.keys(itemsObject);
  const orderedYears = years.sort((a, b) => convertYearIntoNumber(a) - convertYearIntoNumber(b));
  const formatYearPhases = reference => (result, year) => ({
    ...result,
    [year]: reference[year],
  });

  return orderedYears.reduce(formatYearPhases(itemsObject), {});
};


const assignToYearKey = (result, { financial_year: year, amount }) => {
  return {
    ...result,
    [year]: [
      ...(result[year] || []),
      amount,
    ],
  };
};


const normalise = (itemsArray) => {
  const orderedByPhase = forcePhaseOrder(itemsArray);
  const formattedIntoObject = orderedByPhase.reduce(assignToYearKey, {});
  const orderedByYears = forceYearOrder(formattedIntoObject);
  return orderedByYears;
};


const normaliseExpenditurePhase = (data) => {
  const {
    nominal: nominalRaw,
    real: realRaw,
  } = data;

  const nominal = normalise(nominalRaw);
  const real = normalise(realRaw);

  return {
    nominal,
    real,
  };
};


export default normaliseExpenditurePhase;
