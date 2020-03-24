export default function getCkanUrl() {
  return document.getElementsByTagName('body')[0].getAttribute('data-ckan-url');
}
