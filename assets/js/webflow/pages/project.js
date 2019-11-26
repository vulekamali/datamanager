import { formatCurrency } from '../util.js';
import { provinceCode, createTileLayer } from '../maps.js';


function initPointMap(lat, lon) {
  var map = L.map("project-location-map-container")
      .setView([lat, lon], 13);
  createTileLayer().addTo(map);
  return map;
}

function initMuniMap(lat, lon) {
  var map = L.map("project-municipal-context-map-container")
      .setView([lat, lon], 7);
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

export function projectPage() {
  var project = pageData.project;

  // Project definition
  $(".name-field").text(project.name);
  $(".project-number-field").text(project.project_number);
  $(".budget-programme-field").text(project.budget_programme);
  $(".nature-of-investment-field").text(project.nature_of_investment);

  // Administrative details
  $(".primary-funding-source-field").text(project.primary_funding_source);
  $(".funding-status-field").text(project.funding_status);
  $(".province-field").text(project.province);
  $(".department-field").text(project.department);

  // Location
  $("#local-municipality-field").text(project.local_municipality);
  $("#district-municipality-field").text(project.district_municipality);
  $(".coordinates-field").text(project.latitude + ", " + project.longitude);

  // Implementation
  $(".program-implementing-agent-field").text(project.program_implementing_agent);
  $(".principle-agent-field").text(project.principle_agent);
  $(".main-contractor-field").text(project.main_contractor);
  $(".other-service-providers-field").text(project.other_parties);

  // Dates
  $(".status-field").text(project.status);
  $(".start-date-field").text(project.start_date);
  $(".estimated-construction-start-date-field").text(project.estimated_construction_start_date);
  $(".estimated-completion-date-field").text(project.estimated_completion_date);
  $(".contracted-construction-end-date-field").text(project.contracted_construction_end_date);
  $(".estimated-construction-end-date-field").text(project.estimated_construction_end_date);

  // Budgets and spending
  $(".total-project-cost-field").text(formatCurrency(project.total_project_cost));
  $("#total-professional-fees-field").text(formatCurrency(project.total_professional_fees));
  $(".total-construction-costs-field").text(formatCurrency(project.total_construction_costs));
  $(".variation-orders-field").text(formatCurrency(project.variation_orders));
  $("#expenditure-from-previous-years-professional-fees-field").text(formatCurrency(project.expenditure_from_previous_years_professional_fees));
  $(".expenditure-from-previous-years-construction-costs-field").text(formatCurrency(project.expenditure_from_previous_years_construction_costs));
  $(".expenditure-from-previous-years-total-field").text(formatCurrency(project.expenditure_from_previous_years_total));
  $(".project-expenditure-total-field").text(formatCurrency(project.project_expenditure_total));
  $(".main-appropriation-professional-fees-field").text(formatCurrency(project.main_appropriation_professional_fees));
  $(".main-appropriation-construction-costs-field").text(formatCurrency(project.main_appropriation_construction_costs));
  $(".main-appropriation-total-field").text(formatCurrency(project.main_appropriation_total));
  $("#actual-expenditure-q1-field").text(formatCurrency(project.actual_expenditure_q1));
  $("#actual-expenditure-q2-field").text(formatCurrency(project.actual_expenditure_q2));
  $("#actual-expenditure-q3-field").text(formatCurrency(project.actual_expenditure_q3));
  $("#actual-expenditure-q4-field").text(formatCurrency(project.actual_expenditure_q4));

  // Maps and visualisations
  $(".embed-container").css("background-color", "#e1e1e1");

  if (project.latitude !== null & project.longitude !== null) {
    var locationMap = initPointMap(project.latitude, project.longitude);
    var marker = L.marker([project.latitude, project.longitude]).addTo(locationMap);

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
}  // end project page
