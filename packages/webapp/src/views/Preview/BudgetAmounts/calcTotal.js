const calcTotal = (amount) => {
  if (amount > 1 || parseFloat(amount) === 0) {
    return amount.toFixed(0);
  }

  return '< 1';
}

export default calcTotal;
