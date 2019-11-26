export function formatCurrency(decimalString) {
  if (decimalString == null)
    return "";
  return "R " + Math.round(parseFloat(decimalString)).toLocaleString();
}
