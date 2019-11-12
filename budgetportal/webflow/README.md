budgetportal.webflow
====================

![Diagram of how we use Webflow exports with Django](https://docs.google.com/drawings/d/e/2PACX-1vStj7WS2XgSqr_TNU0tr9rHj--b8p8tPicugHmJNn8SRSHKNkVPucR68Ck7YzsOiVOhNALIVDpq907z/pub?w=954&h=482)
[Edit diagram](https://docs.google.com/drawings/d/1OPS4Jm_DSLhUqwZesImuGfOH5Gd3cjfBTKUns1DozLY/edit)

***Webflow HTML, CSS, Javascript and images must not be edited manually***. Those
edits will be overridden on the next import from Webflow.

For this site, we build pages in Webflow, export the HTML, CSS, Javascript and
images, download them as a zip file, and import them into this django app.
The HTML is copied into the `templates` directory, with any changes needed to
request site-specific dependencies and add data to the page. These are then used
as django templates referred to by views. The assets are copied into the `static`
directory and served by the django static system. The import tool amends the
paths to assets to match those needed by the django static file system.

To import a new Webflow export, run the following in the root of the project
directory, where `~/Downloads/vulekamali.webflow(18).zip` is the path to the
latest webflow code export.

```
python bin/import_webflow_export.py ~/Downloads/vulekamali.webflow\(18\).zip budgetportal/webflow/
```

The import script inserts a Script tag to include `static/js/vulekamali-webflow.js`
in all these pages, which is the Javascript we use to insert page data into
the correct fields.


Provincial Infrastructure Project Search page `/infrastructure-projects/provincial`
----------------------------------

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
- `#province-dropdown`
- `#department-dropdown`
- `#status-dropdown`
- `#primary-funding-source-dropdown`
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


Infrastructure Project Detail page `/infrastructure-projects/provincial/<id>-<slug>-<province-slug>`
----------------------------------

Selectors for templating in data: