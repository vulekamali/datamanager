const originalBudgetGroups = [
  'appropriation-bills',
  'budget-highlights',
  'budget-reviews',
  'budget-speeches',
  'division-of-revenue-bills',
  'estimates-of-national-expenditure',
  'estimates-of-provincial-revenue-and-expenditure',
  'provincial-allocations',
  'occasional-budget-documents',
  'people-s-guides',
  'tax-pocket-guides',
];
const adjustedBudgetGroups = [
  'adjusted-estimates-of-national-expenditure',
  'adjusted-estimates-of-provincial-revenue-and-expenditure',
  'adjustments-appropriation-bills',
  'division-of-revenue-amendment-bills',
  'medium-term-budget-policy-statements',
  'medium-term-budget-policy-statement-speeches',
  'rates-and-monetary-amounts-and-amendment-of-revenue-laws-bills',
  'tax-administration-laws-amendment-bills',
  'taxation-laws-amendment-bills',
];

const keyFormats = [
  "", // looks like web pages without custom specified formats are emtpy string
  "PDF",
  "XLS",
  "XLSX",
  "XLSB",
  "DOC",
  "DOCX",
  "Webcast",
  "PPT",
  "PPTX",
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
    government.original.push(...(filterKeyFormats(dataset.resources)));
  if (dataset.groups.some(group => adjustedBudgetGroups.includes(group.name)))
    government.adjusted.push(...(filterKeyFormats(dataset.resources)));
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

function filterKeyFormats(resources) {
  return resources.filter(r => keyFormats.includes(r.format));
}

export { resourcesUrl, resultsToResources, initialResourceGroups }
