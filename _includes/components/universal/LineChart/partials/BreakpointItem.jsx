import { h } from 'preact';
import trimValues from './../../../../utilities/js/helpers/trimValues.js';


export default function BreakpointItem({ styling, totalGroupSpace, rank, fontSize }) {
  const { valueSpace, buffer, padding, labelBreakpoints, maxValue, svgHeight } = styling;
  const iterationValue = maxValue / (labelBreakpoints - 1);
  const iterationPosition = svgHeight / (labelBreakpoints - 1);

  return (

    <text
      x={padding[3] - buffer}
      y={padding[0] + 7 + (iterationPosition * rank)}
      fill="#3f3f3f"
      text-anchor="end"
      font-size={fontSize}
      font-weight="bold"
      font-family="sans-serif"
    >
      R{trimValues(iterationValue * (labelBreakpoints - (rank + 1)), true)}
    </text>
  );
}
