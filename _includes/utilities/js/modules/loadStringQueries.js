import queryString from 'query-string';


function loadStringQueries() {
  const object = queryString.parse(location.search);
  window.vulekamali = {};
  window.vulekamali.qs = object;
}

export default loadStringQueries();
