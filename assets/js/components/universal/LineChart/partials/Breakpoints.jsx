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
        x={0}
        y={padding[0]}
        height={totalGroupSpace}
        width={(padding[3] - buffer)}
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
