export default function filterAccordingToProvince(items, province) {
  if (province !== 'all') {
    return items.filter(({ slug }) => slug === province);
  }

  return items;
}
