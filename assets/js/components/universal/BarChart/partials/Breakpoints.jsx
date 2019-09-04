import { h } from 'preact';
import BreakpointItem from './BreakpointItem.jsx';


export default function Breakpoints({ items, styling, totalGroupSpace }) {
  const { valueSpace, buffer, padding, labelBreakpoints } = styling;
  let breakpointArray = [];

  for (let i = 0; i < labelBreakpoints; i++) {
    breakpointArray.push('');
  }

  return (
    <g className="Graph-verticalLabelList">
      {/* <rect
        x={padding[3] + buffer}
        y={padding[0] + totalGroupSpace + (buffer * 2)}
        height={padding[2] - buffer}
        width={(padding[3] + valueSpace) - padding[1]}
        fill="red"
        opacity="0.5"
      /> */}

      {
        breakpointArray.map((val, index) => {
          return (
            <BreakpointItem rank={index} {...{ styling, totalGroupSpace }} />
          );
        })
      }
    </g>
  );
}
