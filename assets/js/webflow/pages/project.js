import { formatCurrency, coordsAvailable } from '../util.js';
import { provinceCode, createTileLayer } from '../maps.js';
import { reusableLineChart } from 'vulekamali-visualisations/src/charts/line/reusable-line-chart/reusable-line-chart.js';
import { select } from 'd3-selection';


function initPointMap(lat, lon) {
  var map = L.map("project-location-map-container", {
    center: [lat, lon],
    zoom: 13,
    scrollWheelZoom: false,
  });
  createTileLayer().addTo(map);
  return map;
}

function initMuniMap(lat, lon) {
  var map = L.map("project-municipal-context-map-container", {
    center: [lat, lon],
    zoom: 7,
    scrollWheelZoom: false,
  });
  createTileLayer().addTo(map);
  return map;
}

function addProvinceToMap(map, provinceName) {
  $.get("https://mapit.code4sa.org/area/MDB:" + provinceCode[provinceName] +
        "/feature.geojson?generation=2&simplify_tolerance=0.01")
    .done(function(response) {
      var layer = L.geoJSON(response, {
        weight: 1,
        "fillColor": "#66c2a5",
        "fillOpacity": 0.3,
      })
          .addTo(map)
          .bindTooltip(function (layer) {
            return layer.feature.properties.name + " Province";
          }).addTo(map);

      map.fitBounds(layer.getBounds());
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.error( jqXHR, textStatus, errorThrown );
    });
}


function addMuniToMap(map, provinceName, level, muniName) {
  var levelCode = levelToCode[level];
  $.get("https://mapit.code4sa.org/areas/MDB-levels:PR-" + provinceCode[provinceName] +
        "|" + levelCode + ".geojson?generation=2&simplify_tolerance=0.01")
    .done(function(response) {
      var munis = response.features.filter(function(feature) {
        return feature.properties.name === muniName;
      });
      if (munis.length) {
        var muni = munis[0]; // Assume no duplicate names in a province
        var layer = L.geoJSON(muni, {
          weight: 1,
          "fillColor": "#66c2a5",
          "fillOpacity": 0.3,
        })
            .addTo(map)
            .bindTooltip(function (layer) {
              return layer.feature.properties.name + " " + level;
            }).addTo(map);
      } else {
        console.info("Couldn't find muni " + muniName + " by name in province");
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.error( jqXHR, textStatus, errorThrown );
    });
}

var levelToCode = {
  "Local Municipality": "MN",
  "Metro Municipality": "MN",
  "District Municipality": "DC"
};

function updateTextField(selector, text) {
  const match = $(selector);
  if (text === "" || text === null) {
    match.text("Not available");
    match.addClass("no-data");
  } else {
    match.text(text);
    match.removeClass("no-data");
  }
}

function initTimeSeriesChart(chartData) {
  const container = select("#time-series-chart-container");
  const boundingRect = container.node().getBoundingClientRect();

  const chart = reusableLineChart()
        .width(boundingRect.width)
        .height(boundingRect.height);

  container.call(chart.data(chartData.snapshots));

  return chart;
}

export function projectPage(pageData) {
  var project = pageData.project;

  // Project definition
  updateTextField(".name-field", project.name);
  updateTextField(".project-number-field", project.project_number);
  updateTextField(".budget-programme-field", project.budget_programme);
  updateTextField(".nature-of-investment-field", project.nature_of_investment);

  // Administrative details
  updateTextField(".primary-funding-source-field", project.primary_funding_source);
  updateTextField(".funding-status-field", project.funding_status);
  updateTextField(".province-field", project.province);
  if (pageData.department_url) {
    const fieldContainers = $(".department-field");
    fieldContainers.html(`<a class="project-detail_link" href="${pageData.department_url}"></a>`);
    // Set text using .text() to avoid HTML injection
    fieldContainers.find("a").text(project.department);
  } else {
    updateTextField(".department-field", project.department);
  }

  // Location
  updateTextField("#local-municipality-field", project.local_municipality);
  updateTextField("#district-municipality-field", project.district_municipality);
  updateTextField(".coordinates-field",
                  coordsAvailable(project.latitude, project.longitude) ? `${project.latitude}, ${project.longitude}` : null);

  // Implementation
  updateTextField(".program-implementing-agent-field", project.program_implementing_agent);
  updateTextField(".principle-agent-field", project.principle_agent);
  updateTextField(".main-contractor-field", project.main_contractor);
  updateTextField(".other-service-providers-field", project.other_parties);

  // Dates
  updateTextField(".status-field", project.status);
  updateTextField(".start-date-field", project.start_date);
  updateTextField(".estimated-construction-start-date-field",
                  project.estimated_construction_start_date);
  updateTextField(".estimated-completion-date-field",
                  project.estimated_completion_date);
  updateTextField(".contracted-construction-end-date-field",
                  project.contracted_construction_end_date);
  updateTextField(".estimated-construction-end-date-field",
                  project.estimated_construction_end_date);

  // Budgets and spending
  updateTextField(".total-project-cost-field",
                  formatCurrency(project.total_project_cost));
  updateTextField("#total-professional-fees-field",
                  formatCurrency(project.total_professional_fees));
  updateTextField(".total-construction-costs-field",
                  formatCurrency(project.total_construction_costs));
  updateTextField(".variation-orders-field",
                  formatCurrency(project.variation_orders));
  updateTextField("#expenditure-from-previous-years-professional-fees-field",
                  formatCurrency(project.expenditure_from_previous_years_professional_fees));
  updateTextField(".expenditure-from-previous-years-construction-costs-field",
                  formatCurrency(project.expenditure_from_previous_years_construction_costs));
  updateTextField(".expenditure-from-previous-years-total-field",
                  formatCurrency(project.expenditure_from_previous_years_total));
  updateTextField(".project-expenditure-total-field",
                  formatCurrency(project.project_expenditure_total));
  updateTextField(".main-appropriation-professional-fees-field",
                  formatCurrency(project.main_appropriation_professional_fees));
  updateTextField(".main-appropriation-construction-costs-field",
                  formatCurrency(project.main_appropriation_construction_costs));
  updateTextField(".main-appropriation-total-field", formatCurrency(project.main_appropriation_total));
  updateTextField("#actual-expenditure-q1-field", formatCurrency(project.actual_expenditure_q1));
  updateTextField("#actual-expenditure-q2-field", formatCurrency(project.actual_expenditure_q2));
  updateTextField("#actual-expenditure-q3-field", formatCurrency(project.actual_expenditure_q3));
  updateTextField("#actual-expenditure-q4-field", formatCurrency(project.actual_expenditure_q4));

  // Maps and visualisations
  $(".embed-container").css("background-color", "#e1e1e1");

  if (coordsAvailable(project.latitude, project.longitude)) {
    var locationMap = initPointMap(project.latitude, project.longitude);
    var marker = L.marker([project.latitude, project.longitude]).addTo(locationMap);
  } else {
    $("#project-location-map-container .map__no-data").css("display", "flex");
  }

  $.get("https://mapit.code4sa.org/area/MDB:" + provinceCode[project.province] + "/geometry")
    .done(function(response) {
      var muniMap = initMuniMap(response.centre_lat, response.centre_lon);

      addProvinceToMap(muniMap, project.province);

      if (project.district_municipality === project.local_municipality
          & project.district_municipality != null) {
        addMuniToMap(muniMap, project.province, "Metro Municipality", project.local_municipality);
      } else {
        if (project.district_municipality != null)
          addMuniToMap(muniMap, project.province, "District Municipality", project.district_municipality);
        if (project.local_municipality != null)
          addMuniToMap(muniMap, project.province, "Local Municipality", project.local_municipality);
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      console.error(jqXHR, textStatus, errorThrown);
    });

  initTimeSeriesChart(pageData.time_series_chart);
}  // end project page
