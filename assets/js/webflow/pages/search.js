/**************************************************************
 Style vision:
 It would be nice if there weren't a million things updating
 and reading pageState but it seems necessary for event handlers
 to figure out the right thing to do.

 pageState is module-global and initialises fields that will be
 used later.

 searchPage is called only on the search page, and initialises
 things dependent on the page markup.

 Each interaction that should trigger a search updates pageState
 if needed (e.g. if it was a dropdown selection, it updates the
 relevant pageState.filters field) and then calls triggerSearch.

 triggerSearch always looks at the current pageState and starts
 the search requests based on that.

 The success handler of each of the search request updates anything
 it needs to in pageState, and updates the UI to reflect the response
 from the server.

 ajax requests should always cancel the relevant previous request
 if it's still in flight before being sent, and should always have
 an error handler giving some user feedback as well as technical
 information in the console to notice and understand errors.
 /***************************************************************/

import {formatCurrency, statusOrder, sortByOrderArray, sortOptions} from '../util.js';
import {createTileLayer} from '../maps.js';
import {reusableBarChart} from 'vulekamali-visualisations/src/charts/bar/reusable-bar-chart/reusable-bar-chart.js';
import {select} from 'd3-selection';


const pageState = {
    filters: null,
    facetsRequest: null,
    mapPointsRequest: null,
    sortField: null,
    listRequest: null,
    map: null,
    markers: null,
    resultRowTemplate: null,
    dropdownItemTemplate: null,
    statusChart: null,
};

const baseLocation = "/api/v1/infrastructure-projects/full/search/";
const facetsLocation = "/api/v1/infrastructure-projects/full/search/facets/";

const facetPlurals = {
    government_label: "governments",
    sector: "sectors",
    department: "departments",
    status: "project statuses",
    primary_funding_source: "funding sources",
    financial_year: "financial years"
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
    if (textQuery)
        $("#Infrastructure-Search-Input").val(textQuery);

    const filterParams = params.getAll("filter");
    pageState.filters = {};
    filterParams.forEach(param => {
        const pieces = param.split(/:/);
        const key = pieces.shift();
        const val = pieces.join(':');
        pageState.filters[key] = val;
    });

    const sortField = params.get("order_by");
    pageState.sortField = sortField || "status_order";
}

function urlFromSearchState() {
    var params = new URLSearchParams();
    params.set("q", $("#Infrastructure-Search-Input").val());

    for (let fieldName in pageState.filters) {
        params.append("filter", `${fieldName}:${pageState.filters[fieldName]}`);
    }

    params.set("order_by", pageState.sortField);
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

function buildListSearchURL() {
    var params = new URLSearchParams();
    params.set("q", $("#Infrastructure-Search-Input").val());
    for (let fieldName in pageState.filters) {
        params.set(fieldName, pageState.filters[fieldName]);
    }
    params.set("fields", "url_path,name,status,estimated_completion_date,financial_year");
    params.set("limit", "20");
    return baseLocation + "?" + params.toString();
}

function updateFacets() {
    if (pageState.facetsRequest !== null)
        pageState.facetsRequest.abort();
    pageState.facetsRequest = $.get(buildFacetSearchURL())
        .done(function (response) {
            resetFacets();
            showFacetResults(response);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (textStatus !== "abort") {
                alert("Something went wrong when searching. Please try again.");
                console.error(jqXHR, textStatus, errorThrown);
            }
        });
}

function updateMapPoints(url) {
    getLoadingSpinner().show();

    if (pageState.mapPointsRequest !== null) {
        pageState.mapPointsRequest.abort();
    }

    pageState.mapPointsRequest = $.get(url)
        .done(function (response) {
            addMapPoints(response);
            if (response.next) {
                updateMapPoints(response.next);
            } else {
                getLoadingSpinner().hide();
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (textStatus !== "abort") {
                alert("Something went wrong when loading map data. Please try again.");
                console.error(jqXHR, textStatus, errorThrown);
            }
        });
}

function updateResultList(url) {
    if (pageState.listRequest !== null)
        pageState.listRequest.abort();
    pageState.listRequest = $.get(url)
        .done(function (response) {
            populateDownloadCSVButton(response);
            addListResults(response);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (textStatus !== "abort") {
                alert("Something went wrong when searching. Please try again.");
                console.error(jqXHR, textStatus, errorThrown);
            }
        });
}

function addMapPoints(response) {
    var newMarkers = [];
    response.results.forEach(function (project) {
        if (!project.latitude || !project.longitude)
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
const getLoadMoreResultsButton = () => $("#load-more-results-button");
const getAllResultListItems = () => $("#result-list-container .narrow-card_wrapper");

function resetFacets() {
    $("#num-matching-projects-field").text("");
    resetDropdown("#government-dropdown");
    resetDropdown("#department-dropdown");
    resetDropdown("#sector-dropdown");
    resetDropdown("#status-dropdown");
    resetDropdown("#primary-funding-source-dropdown");
}

function resetResultList() {
    getAllResultListItems().remove();
    getNoResultsMessage().hide();
    getLoadMoreResultsButton()
        .hide()
        .off("click");
}

function triggerSearch(pushHistory = true) {
    if (pushHistory)
        pushState();

    updateFacets();

    resetMapPoints();
    updateMapPoints(buildAllCoordinatesSearchURL());

    resetResultList();
    updateResultList(buildListSearchURL());
};

function populateDownloadCSVButton(response) {
    $("#search-results-download-button").attr("href", response.csv_download_url);
}

function addListResults(response) {
    if (response.results.length) {
        getNoResultsMessage().hide();
        response.results.forEach(function (project) {
            var resultItem = pageState.resultRowTemplate.clone();
            resultItem.attr("href", project.url_path);
            resultItem.find(".narrow-card_title").text(project.name);
            resultItem.find(".narrow-card_middle-column:first").text(project.status);
            resultItem.find(".narrow-card_middle-column:last").text(project.estimated_completion_date);
            resultItem.find(".narrow-card_last-column").remove();
            $("#result-list-container").append(resultItem);
        });

        if (response.next) {
            const nextButton = getLoadMoreResultsButton();
            nextButton.off("click");
            nextButton.on("click", (e) => {
                e.preventDefault();
                updateResultList(response.next);
            });
            nextButton.show();
        }
    } else {
        getNoResultsMessage().show();
    }
}

function showFacetResults(response) {
    console.log({response})
    $("#num-matching-projects-field").text(response.objects.count);
    updateDropdown("#government-dropdown", response.fields["government_label"], "government_label");
    updateDropdown("#department-dropdown", response.fields["department"], "department");
    updateDropdown("#sector-dropdown", response.fields["sector"], "sector");
    updateDropdown("#primary-funding-source-dropdown", response.fields["primary_funding_source"], "primary_funding_source");

    const statusOptions = sortByOrderArray(statusOrder, "text", response.fields["status"]);
    updateDropdown("#status-dropdown", response.fields["financial_year"], "financial_year");
    updateStatusChart(statusOptions);
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

function updateDropdown(selector, options, fieldName) {
    const container = $(selector);
    const trigger = container.find(".chart-dropdown_trigger");
    const optionContainer = container.find(".chart-dropdown_list");
    // Replace webflow tap handlers with our own for opening dropdown
    trigger.off("tap")
        .on("click", () => optionContainer.addClass("w--open"));

    const selectedOption = getSelectedOption(fieldName);
    const currentSelectionLabel = container.find(".text-block");

    if (typeof (selectedOption) == "undefined") {
        currentSelectionLabel.text("All " + facetPlurals[fieldName]);
    } else {
        currentSelectionLabel.text(selectedOption);
    }

    // Add "clear filter" option
    const optionElement = pageState.dropdownItemTemplate.clone();
    optionElement.find(".search-dropdown_label").text("All " + facetPlurals[fieldName]);
    optionElement.click(function (e) {
        e.preventDefault();
        delete pageState.filters[fieldName];
        optionContainer.removeClass("w--open");
        triggerSearch();
    });
    optionContainer.append(optionElement);

    options.forEach(function (option) {
        const optionElement = pageState.dropdownItemTemplate.clone();
        optionElement.find(".search-dropdown_label").text(option.text);
        if (option.count) {
            optionElement.find(".search-dropdown_value").text("(" + option.count + ")");
        }
        optionElement.click(function (e) {
            e.preventDefault();
            pageState.filters[fieldName] = option.text;
            optionContainer.removeClass("w--open");
            triggerSearch();
        });
        optionContainer.append(optionElement);
    });
}

function initSortDropdown() {
    const selector = "#sort-order-dropdown";
    const dropdownItemTemplate = $("#sort-order-dropdown * .dropdown-link--small:first");
    dropdownItemTemplate.find(".sorting-status").remove();
    dropdownItemTemplate.find(".dropdown-label").text("");
    $(selector).find(".text-block").text("");
    $(selector).find(".dropdown-link--small").remove();

    var container = $(selector);
    var optionContainer = container.find(".sorting-dropdown_list");

    container.find(".text-block").text(sortOptions.get(pageState.sortField));

    sortOptions.forEach((label, key) => {
        const optionElement = dropdownItemTemplate.clone();
        optionElement.find(".dropdown-label").text(label);
        optionElement.click(function (e) {
            e.preventDefault();
            container.find(".text-block").text(label);
            pageState.sortField = key;
            optionContainer.removeClass("w--open");
            triggerSearch();
        });
        optionContainer.append(optionElement);
    });
}

function initStatusChart() {
    const container = select("#matching-status-chart-container");
    const boundingRect = container.node().getBoundingClientRect();

    const chart = reusableBarChart()
        .width(boundingRect.width)
        .height(boundingRect.height)
        .colors(['#65b344', '#65b344']);
    ;

    container.call(chart);

    chart.padding(80);

    return chart;
}

function updateStatusChart(statusOptions) {
    pageState.statusChart.data(statusOptions.map(item => ({
        "label": item.text,
        "value": item.count ? item.count : 0
    })));
}

export function searchPage(pageData) {

    /** Get templates of dynamically inserted elements **/

    $("#result-list-container .narrow-card_last-header").remove();
    pageState.resultRowTemplate = $("#result-list-container .narrow-card_wrapper:first").clone();
    pageState.resultRowTemplate.find(".narrow-card_icon").remove();

    pageState.dropdownItemTemplate = $("#government-dropdown * .dropdown-link:first");
    pageState.dropdownItemTemplate.find(".search-status").remove();
    pageState.dropdownItemTemplate.find(".search-dropdown_label").text("");
    pageState.dropdownItemTemplate.find(".search-dropdown_value").text("");

    pageState.statusChart = initStatusChart();


    /** initialise stuff **/

    $("#map").empty();
    pageState.map = L.map("map", {
        center: [-30.5595, 22.9375],
        zoom: 4,
        scrollWheelZoom: false
    });
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
    $("#Search-Button").on("click", (e) => {
        e.preventDefault();
        triggerSearch();
    });
    $("#clear-filters-button").on("click", (e) => {
        e.preventDefault();
        clearFilters();
    });
    window.addEventListener("popstate", onPopstate);

    /**
     * Search on page load
     *
     * Ordering may be important based on setting up and depending on pageState.
     */


    resetFacets();
    resetResultList();
    loadSearchStateFromCurrentURL();
    initSortDropdown();
    triggerSearch(false);

} // end search page
