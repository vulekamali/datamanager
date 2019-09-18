export default function trimValues(rawValue, abbreviated) {
  const value = parseInt(rawValue, 10);
  const million = abbreviated ? 'm' : 'million';
  const billion = abbreviated ? 'bn' : 'billion';

  if (value < 1000000 && value > -1000000) {
    return value.toFixed(1).replace(/\.0$/, '');
  }

  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(1).replace(/\.0$/, '')} ${billion}`;
  }

  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1).replace(/\.0$/, '')} ${million}`;
  }

  if (value <= -1000000000) {
    return `${(value / 1000000000).toFixed(1).replace(/\.0$/, '')} ${billion}`;
  }

  if (value <= -1000000) {
    return `${(value / 1000000).toFixed(1).replace(/\.0$/, '')} ${million}`;
  }


  return null;
}
