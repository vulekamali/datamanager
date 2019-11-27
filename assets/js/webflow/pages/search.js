import { formatCurrency } from '../util.js';
import { createTileLayer } from '../maps.js';


const searchState = {
  filters: null,
  facetsRequest: null,
  mapPointsRequest: null,
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
  loadSearchFromURL();
}

function loadSearchFromCurrentURL() {
  const queryString = window.location.search.substring(1);
  const params = new URLSearchParams(queryString);

  const textQuery = params.get("q");
  $("#Infrastructure-Search-Input").val(textQuery);

  const filterParams = params.getAll("filter");
  searchState.filters = {};
  filterParams.forEach(param => {
    const pieces = param.split(/:/);
    const key = pieces.shift();
    const val = pieces.join(':');
    searchState.filters[key] = val;
  });
}


export function searchPage(pageData) {
  loadSearchFromCurrentURL();

  const noResultsMessage = $("#result-list-container * .w-dyn-empty");
  const loadingSpinner = $(".loading-spinner");
  const map = L.map("map").setView([-30.5595, 22.9375], 4);
  const markers = L.markerClusterGroup();


  /** Get templates of dynamically inserted elements **/

  var resultRowTemplate = $("#result-list-container .narrow-card_wrapper:first").clone();
  resultRowTemplate.find(".narrow-card_icon").remove();

  var dropdownItemTemplate = $("#province-dropdown * .dropdown-link:first");
  dropdownItemTemplate.find(".search-status").remove();
  dropdownItemTemplate.find(".search-dropdown_label").text("");
  dropdownItemTemplate.find(".search-dropdown_value").text("");


  /** initialise stuff **/

  $("#map").empty();

  createTileLayer().addTo(searchState.map);
  searchState.map.addLayer(searchState.markers);


  function updateFreeTextParam() {
    searchState.params.set("q", $("#Infrastructure-Search-Input").val());
  }

  function updateFacetParam() {
    searchState.params.delete("selected_facets");
    for (let fieldName in searchState.filters) {
      var paramValue = fieldName + "_exact:" + searchState.filters[fieldName];
      searchState.params.append("selected_facets", paramValue);
    }
  }

  function buildPagedSearchURL() {
    updateFreeTextParam();
    updateFacetParam();
    return facetsLocation + "?" + searchState.params.toString();
  }

  function buildAllCoordinatesSearchURL() {
    var params = new URLSearchParams();
    params.set("q", $("#Infrastructure-Search-Input").val());
    for (let fieldName in searchState.filters) {
      params.set(fieldName, searchState.filters[fieldName]);
    }
    params.set("fields", "url_path,name,latitude,longitude");
    params.set("limit", "1000");
    return baseLocation + "?" + params.toString();
  }

  function resetResults() {
    $("#num-matching-projects-field").text("");
    $("#result-list-container .narrow-card_wrapper").remove();
    resetDropdown("#province-dropdown");
    resetDropdown("#department-dropdown");
    resetDropdown("#status-dropdown");
    resetDropdown("#primary-funding-source-dropdown");
    noResultsMessage.hide();
  }

  function triggerSearch() {
    if (searchState.facetsRequest !== null)
      searchState.facetsRequest.abort();
    searchState.facetsRequest = $.get(buildPagedSearchURL())
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
    resetMapPoints();
    getMapPoints(buildAllCoordinatesSearchURL());
  }

  function getMapPoints(url) {
    loadingSpinner.show();
    if (searchState.mapPointsRequest !== null)
      searchState.mapPointsRequest.abort();
    searchState.mapPointsRequest = $.get(url)
      .done(function(response) {
        addMapPoints(response);
        if (response.next) {
          getMapPoints(response.next);
        } else {
          loadingSpinner.hide();
        }
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        if (textStatus !== "abort") {
          alert("Something went wrong when loading map data. Please try again.");
          console.error( jqXHR, textStatus, errorThrown );
        }
      });
  }

  function showResults(response) {
    $("#num-matching-projects-field").text(response.objects.count);
    updateDropdown("#province-dropdown", response.fields, "province");
    updateDropdown("#department-dropdown", response.fields, "department");
    updateDropdown("#status-dropdown", response.fields, "status");
    updateDropdown("#primary-funding-source-dropdown", response.fields, "primary_funding_source");

    if (response.objects.results.length) {
      noResultsMessage.hide();
      response.objects.results.forEach(function(project) {
        var resultItem = resultRowTemplate.clone();
        resultItem.attr("href", project.url_path);
        resultItem.find(".narrow-card_title").text(project.name);
        resultItem.find(".narrow-card_middle-column:first").text(project.status);
        resultItem.find(".narrow-card_middle-column:last").text(project.estimated_completion_date);
        resultItem.find(".narrow-card_last-column").text(formatCurrency(project.total_project_cost));
        $("#result-list-container").append(resultItem);
      });
    } else {
      noResultsMessage.show();
    }
  }

  function resetMapPoints() {
    searchState.markers.clearLayers();
  }

  function addMapPoints(response) {
    var markers = [];
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
      markers.push(marker);
    });
    if (markers.length) {
      searchState.markers.addLayers(markers);
      searchState.map.fitBounds(searchState.markers.getBounds());
    }
  }

  function resetDropdown(selector) {
    $(selector).find(".text-block").text("");
    $(selector).find(".dropdown-link").remove();
  }

  function getSelectedOption(fieldName) {
    return searchState.filters[fieldName];
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
      const optionElement = dropdownItemTemplate.clone();
      optionElement.find(".search-dropdown_label").text("All " + facetPlurals[fieldName]);
      optionElement.click(function() {
        delete searchState.filters[fieldName];
        optionContainer.removeClass("w--open");
        triggerSearch();
      });
      optionContainer.append(optionElement);
    }

    var options = fields[fieldName];
    fields[fieldName].forEach(function (option) {
      const optionElement = dropdownItemTemplate.clone();
      optionElement.find(".search-dropdown_label").text(option.text);
      if (option.count) {
        optionElement.find(".search-dropdown_value").text("(" + option.count + ")");
      }
      optionElement.click(function() {
        searchState.filters[fieldName] = option.text;
        optionContainer.removeClass("w--open");
        triggerSearch();
      });
      optionContainer.append(optionElement);
    });
  }


  /** Set up search triggering events **/

  $("#Infrastructure-Search-Input").keypress(function (e) {
    var key = e.which;
    if (key == 13) {  // the enter key code
      triggerSearch();
    }
  });
  $("#Search-Button").on("click", triggerSearch);


  /** Search on page load **/

  resetResults();
  triggerSearch();

} // end search page
