import breakIntoWrap from './breakIntoWrap.js';


export default function buildGroupSpaceArray(items, styling) {
  const {
    lineGutter,
    barWidth,
    groupMargin,
    charWrap,
    charLineHeight,
    titleSpace,
  } = styling;

  return Object.keys(items).map((key) => {
    const value = items[key];
    const rawLines = breakIntoWrap(key, charWrap);

    const lines = rawLines.filter((val) => {
      return val !== '';
    });

    const totalGutters = (value.length - 1) * lineGutter;
    const totalLineWidth = value.length * barWidth;
    const totalText = charLineHeight * lines.length;

    return totalGutters + totalLineWidth + totalText + groupMargin;
  });
}
