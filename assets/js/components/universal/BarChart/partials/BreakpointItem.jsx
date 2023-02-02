import React from 'react';
import trimValues from './../../../../utilities/js/helpers/trimValues.js';


export default function HorisontalBreakpoint({ styling, totalGroupSpace, rank }) {
  const { maxValue, fontSize, valueSpace, buffer, padding, labelBreakpoints } = styling;
  const debugIteration = (valueSpace - buffer) / labelBreakpoints;
  const iterationValue = maxValue / (labelBreakpoints - 1);
  const iterationPosition = (valueSpace - buffer) / (labelBreakpoints - 1);

  return (
    <g>
      {/* <rect
        x={padding[3] + buffer + (rank * debugIteration)}
        y={padding[0] + totalGroupSpace + (buffer * 2)}
        height={padding[2] - buffer}
        width={debugIteration}
        fill="none"
        stroke="red"
        opacity="0.5"
      /> */}

      <text
        className="Graph-label"
        x={padding[3] + buffer + (rank * iterationPosition)}
        y={padding[0] + totalGroupSpace + (buffer * 2) + fontSize}
        font-size={fontSize}
        font-family="sans-serif"
        font-weight="bold"
        text-anchor="middle"
      >
        R{trimValues(iterationValue * rank)}
      </text>
    </g>
  );
}
