const originalBudgetGroups = [
  'estimates-of-provincial-revenue-and-expenditure',
  'people-s-guides',
  'occasional-budget-documents',
  'tax-pocket-guides',
  'appropriation-bills',
  'budget-highlights',
  'budget-reviews',
  'budget-speeches',
  'division-of-revenue-bills',
  'estimates-of-national-expenditure',
];
const adjustedBudgetGroups = [
  'adjusted-estimates-of-national-expenditure',
  'adjusted-estimates-of-provincial-revenue-and-expenditure',
  'division-of-revenue-amendment-bills',
  'adjustments-appropriation-bills',
  'medium-term-budget-policy-statements',
];

const governments = [
  "South Africa",
  "Eastern Cape",
  "Free State",
  "Gauteng",
  "KwaZulu-Natal",
  "Limpopo",
  "Mpumalanga",
  "North West",
  "Northern Cape",
  "Western Cape",
];

function initialResourceGroups() {
  return initialiseResourceGroups(() => null);
}
function emptyResourceGroups() {
  return initialiseResourceGroups(() => []);
}
function initialiseResourceGroups(valueFunction) {
  return governments.reduce((groups, gov) => {
    groups[gov] = {"original": valueFunction(), "adjusted": valueFunction()};
    return groups;
  }, {});
}

function resourcesUrl(ckanUrl, financialYear) {
  const groupsClause = [...originalBudgetGroups, ...adjustedBudgetGroups]
        .map(g => `groups:"${g}"`)
        .join(' OR ');
  const fqParams = [
    'organization:"national-treasury"',
    `(${groupsClause})`,
    `vocab_financial_years:"${financialYear}"`,
  ].join('+');
  const searchParams = new URLSearchParams();
  searchParams.set('q', '');
  searchParams.set('fq', fqParams);
  searchParams.set('rows', '1000');
  return `${ckanUrl}/api/3/action/package_search?${searchParams.toString()}`;
}

/**
 * @param {array} results - CKAN package_search action results field: an array of packages.

 * Returns an object keyed by government name, where the values are objects
 * with that government's budgetResources and adjustedBudgetResources as keys.
 */
function resultsToResources(results) {
  return results.reduce(datasetReducer, emptyResourceGroups());
}

function datasetReducer(governments, dataset) {
  const governmentName = datasetGovernment(dataset);
  if (governmentName === null) {
    console.warn("Unknown government", dataset);
    return governments;
  }
  const government = governments[governmentName];
  if (dataset.groups.some(group => originalBudgetGroups.includes(group.name)))
    government.original.push(...(dataset.resources));
  if (dataset.groups.some(group => adjustedBudgetGroups.includes(group.name)))
    government.adjusted.push(...(dataset.resources));
  return governments;
}

function datasetGovernment(dataset) {
  if (dataset.sphere.length > 1) {
    console.error("More than one sphere", dataset);
    return null;
  }
  if (dataset.sphere[0] === "national")
      return "South Africa";
  if (dataset.sphere[0] === "provincial") {
    if (dataset.province.length > 1)
      console.error("More than one province", dataset);
    return dataset.province[0];
  }
  return null;
}

export { resourcesUrl, resultsToResources, initialResourceGroups }
