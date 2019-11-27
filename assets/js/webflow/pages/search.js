/**************************************************************
  Style vision:
    Starting to move things out of searchPage, binding
    data and functions dependent on page-specific variables
    to pageState so that they can be reached from smaller
    functions.
    I think searchPage should as far as possible just bind variables
    and event listeners for page elements and trigger ajax calls
    needed on page load.
/***************************************************************/

import { formatCurrency } from '../util.js';
import { createTileLayer } from '../maps.js';


const pageState = {
  filters: null,
  facetsRequest: null,
  mapPointsRequest: null,
  map: null,
  markers: null,
  resultRowTemplate: null,
  dropdownItemTemplate: null,
};

const baseLocation = "/api/v1/infrastructure-projects/provincial/search/";
const facetsLocation = "/api/v1/infrastructure-projects/provincial/search/facets/";

const facetPlurals = {
  province: "provinces",
  department: "departments",
  status: "project statuses",
  primary_funding_source: "funding sources",
};

function onPopstate(event) {
  loadSearchStateFromCurrentURL();
  triggerSearch(false);
}

function pushState() {
  window.history.pushState(null, "", urlFromSearchState());
}

function loadSearchStateFromCurrentURL() {
  const queryString = window.location.search.substring(1);
  const params = new URLSearchParams(queryString);

  const textQuery = params.get("q");
  $("#Infrastructure-Search-Input").val(textQuery);

  const filterParams = params.getAll("filter");
  pageState.filters = {};
  filterParams.forEach(param => {
    const pieces = param.split(/:/);
    const key = pieces.shift();
    const val = pieces.join(':');
    pageState.filters[key] = val;
  });
}

function urlFromSearchState() {
  var params = new URLSearchParams();
  params.set("q", $("#Infrastructure-Search-Input").val());

  for (let fieldName in pageState.filters) {
    params.append("filter", `${fieldName}:${pageState.filters[fieldName]}`);
  }
  const queryString = params.toString();
  return `${window.location.protocol}//${window.location.host}${window.location.pathname}?${queryString}`;
}

function clearFilters() {
  pageState.filters = {};
  $("#Infrastructure-Search-Input").val("");
  triggerSearch();
}

function buildFacetSearchURL() {
  var params = new URLSearchParams();
  params.set("q", $("#Infrastructure-Search-Input").val());
  for (let fieldName in pageState.filters) {
    var paramValue = fieldName + "_exact:" + pageState.filters[fieldName];
    params.append("selected_facets", paramValue);
  }
  return facetsLocation + "?" + params.toString();
}

function buildAllCoordinatesSearchURL() {
  var params = new URLSearchParams();
  params.set("q", $("#Infrastructure-Search-Input").val());
  for (let fieldName in pageState.filters) {
    params.set(fieldName, pageState.filters[fieldName]);
  }
  params.set("fields", "url_path,name,latitude,longitude");
  params.set("limit", "1000");
  return baseLocation + "?" + params.toString();
}

function updateFacets() {
  if (pageState.facetsRequest !== null)
    pageState.facetsRequest.abort();
  pageState.facetsRequest = $.get(buildFacetSearchURL())
    .done(function(response) {
      resetResults();
      showResults(response);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      if (textStatus !== "abort") {
        alert("Something went wrong when searching. Please try again.");
        console.error( jqXHR, textStatus, errorThrown );
      }
    });
}

function updateMapPoints(url) {
  getLoadingSpinner().show();

  if (pageState.mapPointsRequest !== null) {
    pageState.mapPointsRequest.abort();
  }

  pageState.mapPointsRequest = $.get(url)
    .done(function(response) {
      addMapPoints(response);
      if (response.next) {
        getMapPoints(response.next);
      } else {
        getLoadingSpinner().hide();
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      if (textStatus !== "abort") {
        alert("Something went wrong when loading map data. Please try again.");
        console.error( jqXHR, textStatus, errorThrown );
      }
    });
}

function addMapPoints(response) {
  var newMarkers = [];
  response.results.forEach(function(project) {
    if (! project.latitude || ! project.longitude)
      return;

    var latitude = parseFloat(project.latitude);
    if (latitude < -34.5916 || latitude > -21.783733) {
      console.log("Ignoring latitude " + latitude);
      return;
    }

    var longitude = parseFloat(project.longitude);
    if (longitude < 14.206737 || longitude > 33.074960) {
      console.log("Ignoring longitude " + longitude);
      return;
    }

    var marker = L.marker([latitude, longitude])
        .bindPopup(project.name + '<br><a target="_blank" href="' +
                   project.url_path + '">Jump to project</a>');
    newMarkers.push(marker);
  });
  if (newMarkers.length) {
    pageState.markers.addLayers(newMarkers);
    pageState.map.fitBounds(pageState.markers.getBounds());
  }
}

const getLoadingSpinner = () => $(".loading-spinner");
const getNoResultsMessage = () => $("#result-list-container * .w-dyn-empty");

function resetResults() {
  $("#num-matching-projects-field").text("");
  $("#result-list-container .narrow-card_wrapper").remove();
  resetDropdown("#province-dropdown");
  resetDropdown("#department-dropdown");
  resetDropdown("#status-dropdown");
  resetDropdown("#primary-funding-source-dropdown");
  getNoResultsMessage().hide();
}

function triggerSearch(pushHistory = true) {
  if (pushHistory)
    pushState();

  updateFacets();
  resetMapPoints();
  updateMapPoints(buildAllCoordinatesSearchURL());
};

function showResults(response) {
  $("#num-matching-projects-field").text(response.objects.count);
  updateDropdown("#province-dropdown", response.fields, "province");
  updateDropdown("#department-dropdown", response.fields, "department");
  updateDropdown("#status-dropdown", response.fields, "status");
  updateDropdown("#primary-funding-source-dropdown", response.fields, "primary_funding_source");

  if (response.objects.results.length) {
    getNoResultsMessage().hide();
    response.objects.results.forEach(function(project) {
      var resultItem = pageState.resultRowTemplate.clone();
      resultItem.attr("href", project.url_path);
      resultItem.find(".narrow-card_title").text(project.name);
      resultItem.find(".narrow-card_middle-column:first").text(project.status);
      resultItem.find(".narrow-card_middle-column:last").text(project.estimated_completion_date);
      resultItem.find(".narrow-card_last-column").text(formatCurrency(project.total_project_cost));
      $("#result-list-container").append(resultItem);
    });
  } else {
    getNoResultsMessage().show();
  }
}

function resetMapPoints() {
  pageState.markers.clearLayers();
}

function resetDropdown(selector) {
  $(selector).find(".text-block").text("");
  $(selector).find(".dropdown-link").remove();
}

function getSelectedOption(fieldName) {
  return pageState.filters[fieldName];
}

function updateDropdown(selector, fields, fieldName) {
  var container = $(selector);
  var optionContainer = container.find(".chart-dropdown_list");

  var selectedOption = getSelectedOption(fieldName);
  if (typeof(selectedOption) == "undefined") {
    container.find(".text-block").text("All " + facetPlurals[fieldName]);
  } else {
    container.find(".text-block").text(selectedOption);
    // Add "clear filter" option
    const optionElement = pageState.dropdownItemTemplate.clone();
    optionElement.find(".search-dropdown_label").text("All " + facetPlurals[fieldName]);
    optionElement.click(function() {
      delete pageState.filters[fieldName];
      optionContainer.removeClass("w--open");
      triggerSearch();
    });
    optionContainer.append(optionElement);
  }

  var options = fields[fieldName];
  fields[fieldName].forEach(function (option) {
    const optionElement = pageState.dropdownItemTemplate.clone();
    optionElement.find(".search-dropdown_label").text(option.text);
    if (option.count) {
      optionElement.find(".search-dropdown_value").text("(" + option.count + ")");
    }
    optionElement.click(function() {
      pageState.filters[fieldName] = option.text;
      optionContainer.removeClass("w--open");
      triggerSearch();
    });
    optionContainer.append(optionElement);
  });
}

export function searchPage(pageData) {

  /** Get templates of dynamically inserted elements **/

  pageState.resultRowTemplate = $("#result-list-container .narrow-card_wrapper:first").clone();
  pageState.resultRowTemplate.find(".narrow-card_icon").remove();

  pageState.dropdownItemTemplate = $("#province-dropdown * .dropdown-link:first");
  pageState.dropdownItemTemplate.find(".search-status").remove();
  pageState.dropdownItemTemplate.find(".search-dropdown_label").text("");
  pageState.dropdownItemTemplate.find(".search-dropdown_value").text("");


  /** initialise stuff **/

  $("#map").empty();
  pageState.map = L.map("map").setView([-30.5595, 22.9375], 4);
  pageState.markers = L.markerClusterGroup();
  createTileLayer().addTo(pageState.map);
  pageState.map.addLayer(pageState.markers);


  /** Set up search triggering events **/

  $("#Infrastructure-Search-Input").keypress(function (e) {
    var key = e.which;
    if (key == 13) {  // the enter key code
      triggerSearch();
    }
  });
  $("#Search-Button").on("click", triggerSearch);
  $("#clear-filters-button").on("click", clearFilters);
  window.addEventListener("popstate", onPopstate);

  /** Search on page load **/

  loadSearchStateFromCurrentURL();
  resetResults();
  triggerSearch(false);

} // end search page
