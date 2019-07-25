export default function decodeHtmlEntities(input) {
  let element = document.createElement('div');
  element.innerHTML = input;

  return element.childNodes.length === 0 ? '' : element.childNodes[0].nodeValue;
}
