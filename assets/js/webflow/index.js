import { searchPage } from './pages/search.js';
import { projectPage } from './pages/project.js';
// Webflow pages include jQuery so we don't needt to import that

$(document).ready(function() {
  if ($("body.provincial-infrastructure-project-detail-page").length) {
    projectPage();
  };

  if ($("#Infrastructure-Search-Input").length) {
    searchPage();
  }
});
