import React from 'react';
import TooltipItem from './TooltipItem.jsx';
import breakIntoWrap from './breakIntoWrap.js';

const colours = [
  '#79b43c',
  '#4a4a4a',
  '#ad3c64',
];

export default function TooltipGroup({ totalGroupSpace, items, groupSpaceArray, rank, lines, title, styling, purple }) {
  const {
    barWidth,
    padding,
    buffer,
    valueSpace,
    lineGutter,
    maxValue,
    groupMargin,
    charLineHeight,
    titleSpace,
    charWrap,
  } = styling;

  const groupSpace = groupSpaceArray[rank];

  const previousSpace = groupSpaceArray.reduce(
    (result, val, index) => {
      if (index < rank) {
        return result + val;
      }

      return result;
    },
    0,
  );

  const startPoint = padding[0] + previousSpace;

  const breakIntoArray = (string) => {
    let result = [];

    for (let i = 0; i < string.length; i += charWrap) {
      result.push(string.substr(i, charWrap));
    }

    return result;
  };

  const titles = Object.keys(items);

  return (
    <g className="Graph-group">
      {/* <rect
        x={padding[3] + buffer}
        y={padding[0] + previousSpace}
        width={valueSpace - buffer}
        height={groupSpace}
        fill="none"
        stroke="red"
        opacity="1"
      /> */}

      {
        lines.map((amount, index) => {
          const rawCharArray = breakIntoWrap(title, charWrap);
          const charArray = rawCharArray.filter(val => val !== '');
          const relativeAmount = ((amount / maxValue) * valueSpace) - barWidth;
          const displayAmount = relativeAmount < (barWidth * 2) ? (barWidth * 2) : relativeAmount;

          return (
            <TooltipItem
              {...{ styling }}
              xPosition={(padding[3] + buffer + displayAmount) - (barWidth / 2)}
              yPosition={(groupMargin / 2) + startPoint + (index * (barWidth + lineGutter)) + (barWidth / 2) + (charLineHeight * charArray.length)}
              {...{ amount, totalGroupSpace }}
              colour={purple ? '#ad3c64' : colours[index]}
            />
          );
        })
      }

    </g>
  );
}
