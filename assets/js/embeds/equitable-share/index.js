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
        return getAllocationBySphere(ckanUrl, resource.id);
      } else {
        throw "Data resource not found";
      }
    })
    .then(function(data) {
      console.log(data);
      drawChart(data.result.records);
    })
    .fail(function(jqXHR) {
      console.log("Error getting data for chart", jqXHR);
      sphereChartContainer.text("Error getting data for chart");
    });
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

function getAllocationBySphere(ckanUrl, resourceId) {
  const sqlQuery = `\
SELECT sum(amount_rand_thousand) as amount_rand_thousand, sphere \
FROM "${resourceId}" \
GROUP BY sphere \
ORDER BY sphere`;
  const data = {"sql": sqlQuery};
  const queryUrl = `${ckanUrl}/api/3/action/datastore_search_sql`;
  return $.get(queryUrl, data);
}
