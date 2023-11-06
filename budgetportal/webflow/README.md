Webflow frontend in this Django app
====================

![Diagram of how we use Webflow exports with Django](https://docs.google.com/drawings/d/e/2PACX-1vStj7WS2XgSqr_TNU0tr9rHj--b8p8tPicugHmJNn8SRSHKNkVPucR68Ck7YzsOiVOhNALIVDpq907z/pub?w=954&h=482)
[Edit diagram](https://docs.google.com/drawings/d/1OPS4Jm_DSLhUqwZesImuGfOH5Gd3cjfBTKUns1DozLY/edit)

***Webflow HTML, CSS, Javascript and images must not be edited manually***. Those
edits will be overridden on the next import from Webflow.

For this site, we build pages in Webflow, export the HTML, CSS, Javascript and
images, download them as a zip file, and import them into this django app using 
the [import-webflow-export](https://www.npmjs.com/package/import-webflow-export)
utility.

The HTML is copied into the `templates` directory, with any changes needed to
request site-specific dependencies and add data to the page. These are then used
as django templates referred to by views. The assets are copied into the `static`
directory and served by the django static system. The import tool amends the
paths to assets to match those needed by the django static file system.

To import a new Webflow export, run the following in the root of the project
directory, where `~/Downloads/vulekamali.webflow(18).zip` is the path to the
latest webflow code export.

```
yarn run import-webflow ~/Downloads/vulekamali.webflow\(18\).zip budgetportal/webflow/
```

The import script inserts a Script tag to include `static/js/vulekamali-webflow.js`
in all these pages, which is the Javascript we use to insert page data into
the correct fields.


Infrastructure Project Search page
----------------------------------

- Route: `/infrastructure-projects/full`
- Webflow page name: `Infrastructure Search Template`
- Template File name: `infrastructure-search-template.html`

This page primarily uses the API to fetch and display data.
At the time of writing, the main reason for this is that the design appends
paginated data to the page. Changing search criteria could just as well
trigger a new page load with the server templating in facet data and the first
page of search results. We just went with AJAX for all search results because
subsequent pages would need to be based on the same query as the first page.
Slow stuff like loading map points should be asynchronous client-side requests.

Selectors for templating in data:

- `#Infrastructure-Search-Input`
- `#Search-Button`
- `#clear-filters-button`
- `#government-dropdown`
- `#department-dropdown`
- `#status-dropdown`
- `#funding-source-dropdown`
- `#num-matching-projects-field`
- `#matching-projects-total-cost-field`
- `#matching-projects-total-cost-units-field`
- `#matching-status-chart-container`
- `#sort-order-dropdown`
- `#result-list-container` Result list
  - `.narrow-card_wrapper` Result item
    - `.narrow-card_icon`
    - `.narrow-card_title`
    - `.narrow-card_middle-column` project status
    - `.narrow-card_middle-column` completion date
    - `.narrow-card_last-column` value
- `#load-more-results-button`


Infrastructure Project Detail page
----------------------------------

- Route: `/infrastructure-projects/full/<id>-<slug>-<government-slug>`
- Webflow page name: `Infrastructure Project`
- Template file name: `detail_infrastructure-projects.html`

Selectors for templating in data:

- `body.infrastructure-project-detail-page`
- `#project-location-map-container`
- `#project-municipal-context-map-container`
- Project definition
  - `.name-field`
  - `.project-number-field`
  - `.budget-programme-field`
  - `.nature-of-investment-field`
- Administrative details
  - `.primary-funding-source-field`
  - `.funding-status-field`
  - `.province-field`
  - `.department-field`
- Location
  - `.local-municipality-field`
  - `.district-municipality-field`
  - `.coordinates-field`
- Implementation
  - `.program-implementing-agent-field`
  - `.principle-agent-field`
  - `.main-contractor-field`
  - `.other-service-providers-field`
- Dates
  - `.status-field`
  - `.start-date-field`
  - `.estimated-construction-start-date-field`
  - `.estimated-completion-date-field`
  - `.contracted-construction-end-date-field`
  - `.estimated-construction-end-date-field`
- Budgets and spending
  - `.total-project-cost-field`
  - `.total-professional-fees-field`
  - `.total-construction-costs-field`
  - `.variation-orders-field`
  - `.expenditure-from-previous-years-professional-fees-field`
  - `.expenditure-from-previous-years-construction-costs-field`
  - `.expenditure-from-previous-years-total-field`
  - `.project-expenditure-total-field`
  - `.main-appropriation-professional-fees-field`
  - `.adjustment-appropriation-professional-fees-field`
  - `.main-appropriation-construction-costs-field`
  - `.adjustment-appropriation-construction-costs-field`
  - `.main-appropriation-total-field`
  - `.adjustment-appropriation-total-field`
  - `.actual-expenditure-q1-field`
  - `.actual-expenditure-q2-field`
  - `.actual-expenditure-q3-field`
  - `.actual-expenditure-q4-field`
