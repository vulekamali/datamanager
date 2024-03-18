export default function filterDepartments(items, selected) {
  if (selected !== "all") {
    return items.filter(({ department }) => selected === department);
  }

  return items;
}
