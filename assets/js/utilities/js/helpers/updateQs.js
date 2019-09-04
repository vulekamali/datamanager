import queryString from 'query-string';


export default function updateQs(object) {
  window.vulekamali.qs = object;

  window.history.replaceState(
    null,
    document.title,
    `${window.location.href.split('?')[0]}?${queryString.stringify(object)}`,
  );
}
