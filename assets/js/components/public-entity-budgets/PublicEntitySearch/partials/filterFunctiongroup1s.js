export default function filterFunctiongroup1s(items, functiongroup1) {
  if (functiongroup1 !== "all") {
    return items.filter(
      ({ functiongroup1 }) => functiongroup1 === functiongroup1
    );
  }

  return items;
}
