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
  const sqlQuery = `SELECT * from "${resourceId}" WHERE sphere = 'local'`;
  const queryUrl = `${ckanUrl}/api/3/action/datastore_search_sql?sql=${sqlQuery}`;
};
