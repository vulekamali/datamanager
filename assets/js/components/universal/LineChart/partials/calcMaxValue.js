export default function calcMaxValue(items) {
  const labels = Object.keys(items);

  return labels.reduce(
    (result, key) => {
      const maxValue = Math.max(...items[key]);
      return maxValue > result ? maxValue : result;
    },
    0,
  );
}
