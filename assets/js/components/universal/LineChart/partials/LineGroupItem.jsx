import React from 'react';

const colours = [
  '#79b43c',
  '#4a4a4a',
  '#ad3c64',
];

export default function LineGroupItem({ totalGroupSpace, groupSpaceArray, rank, lines, title, styling }) {
  const {
    barWidth,
    padding,
    buffer,
    lineGutter,
    valueSpace,
    maxValue,
    svgHeight,
  } = styling;

  const groupSpace = groupSpaceArray[rank];

  const generateToScale = (value) => {
    return ((valueSpace - buffer) / totalGroupSpace) * value;
  };

  const previousSpace = groupSpaceArray.reduce(
    (result, val, index) => {
      if (index < rank) {
        return result + generateToScale(val);
      }

      return result;
    },
    0,
  );

  const usedSpace = lines.length * (barWidth + lineGutter);
  const startPoint = padding[3] + buffer + previousSpace;
  const centeringSpace = ((generateToScale(groupSpace) + barWidth) - usedSpace) / 2;


  return (
    <g className="Graph-group">

      {/* <rect
        x={padding[3] + buffer + previousSpace}
        y={padding[0]}
        width={generateToScale(groupSpace)}
        height={totalGroupSpace}
        fill="none"
        stroke="red"
        opacity="1"
      /> */}

      {
        lines.map((amount, index) => {
          const relativeAmount = (amount / maxValue) * svgHeight;
          const displayAmount = relativeAmount < barWidth + 1 ? barWidth + 1 : relativeAmount;
          return (
            <line
              stroke-linecap="round"
              stroke-width={barWidth}
              x1={startPoint + centeringSpace + (index * (barWidth + lineGutter))}
              y1={(padding[0] + svgHeight) - (barWidth / 2)}
              x2={startPoint + centeringSpace + (index * (barWidth + lineGutter))}
              y2={(padding[0] + svgHeight + barWidth) - (barWidth / 2) - displayAmount}
              className="Graph-line"
              stroke="#ad3c64"
            />
          );
        })
      }
    </g>
  );
}
