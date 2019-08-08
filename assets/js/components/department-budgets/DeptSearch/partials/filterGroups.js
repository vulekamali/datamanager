export default function filterAccordingToSphere(items, group, remove) {

  if (remove) {
    return items.filter(({ slug }) => slug !== group);
  }

  return items.filter(({ slug }) => slug === group);
}
