import $ from 'jquery';

$(document).ready(function() {
  const sphereChartContainer = $("#embed-allocation-of-equitable-share-by-sphere");
  if (sphereChartContainer.length) {
    initAllocationBySphere(sphereChartContainer);
  }
});

function initAllocationBySphere(sphereChartContainer) {
  sphereChartContainer.text("Loading...");
  const ckanUrl = $("body").data("ckan-url");

  getDataset(ckanUrl)
    .then(function(data) {
      const datasets = data.result.results;
      sortDatasetsFinYear(datasets);
      console.log(datasets);
      const resource = getLatestAllocationsResource(datasets);
      if (resource) {
        return getAllocationBySphere(ckanUrl);
      } else {
        throw "Data resource not found";
      }
    })
    .then(function(data) {
      drawChart(data);
    })
    .fail(function(jqXHR) {
      console.log("Error getting data for chart", jqXHR);
      sphereChartContainer.text("Error getting data for chart");
    });

  const sqlQuery = `SELECT * from "${resourceId}" WHERE sphere = 'local'`;
  const queryUrl = `${ckanUrl}/api/3/action/datastore_search_sql?sql=${sqlQuery}`;
};

function getDataset(ckanUrl) {
  const packageSearchUrl = `${ckanUrl}/api/action/package_search`;
  const searchParams = {
    "q": "",
    "fq": '+organization:"national-treasury"' +
      'groups:"division-of-revenue-bills"',
  };
  return $.get(packageSearchUrl, searchParams);
}

function getLatestAllocationsResource(datasets) {
  let allocationsResource = null;
  datasets.forEach(function (dataset) {
    dataset.resources.forEach(function (resource) {
      if (resource.name === "Allocation of Equitable Share") {
        allocationsResource = resource;
      }
    });
  });

  return allocationsResource;
}

function sortDatasetsFinYear(datasets) {
  datasets.sort((a, b) => {
    const yearA = a.financial_year || null;
    const yearB = b.financial_year || null;
    if (yearA < yearB)
      return -1;
    else if (yearA === yearB)
      return 0;
    else
      return 1;
  });
}
