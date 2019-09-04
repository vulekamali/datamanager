import { h } from 'preact';
import TooltipItem from './TooltipItem.jsx';

const colours = [
  '#79b43c',
  '#4a4a4a',
  '#ad3c64',
];


export default function TooltipGroup({ totalGroupSpace, groupSpaceArray, rank, lines, title, styling }) {
  const {
    barWidth,
    padding,
    buffer,
    lineGutter,
    valueSpace,
    maxValue,
    popUpOffset,
    popupHeight,
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
        y={0}
        width={generateToScale(groupSpace)}
        height={totalGroupSpace + padding[0]}
        fill="none"
        stroke="red"
        opacity="1"
      /> */}

      {
        lines.map((amount, index) => {
          const relativeAmount = (amount / maxValue) * svgHeight;
          const displayAmount = relativeAmount < barWidth + 1 ? barWidth + 1 : relativeAmount;
          return (
            <TooltipItem
              {...{ styling }}
              xPosition={startPoint + centeringSpace + (index * (barWidth + lineGutter))}
              yPosition={(padding[0] + svgHeight + barWidth) - ((barWidth * 2) + displayAmount + popUpOffset + popupHeight)}
              {...{ amount, totalGroupSpace }}
              colour="#ad3c64"
            />
          );
        })
      }
    </g>
  );
}
