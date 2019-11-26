import { searchPage } from './pages/search.js';
import { projectPage } from './pages/project.js';
// Webflow pages include jQuery so we don't needt to import that

$(document).ready(function() {
  const pageData = JSON.parse(document.getElementById('page-data').textContent);

  if ($("body.provincial-infrastructure-project-detail-page").length) {
    projectPage(pageData);
  };

  if ($("#Infrastructure-Search-Input").length) {
    searchPage(pageData);
  }
});
