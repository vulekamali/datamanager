import { h } from 'preact';


export default function GuideItem({ styling, totalGroupSpace, rank }) {
  const { valueSpace, buffer, fontSize, padding, labelBreakpoints, svgHeight } = styling;
  const iteration = svgHeight / (labelBreakpoints - 1);

  // const debugIteration = totalGroupSpace / labelBreakpoints;

  return (
    <g>
      {/* <rect
        x={padding[3] + buffer}
        y={padding[0] + (rank * debugIteration)}
        height={debugIteration}
        width={padding[3] - buffer}
        fill="none"
        stroke="blue"
        opacity="0.5"
      /> */} 

      <line
        x1={padding[3]}
        y1={padding[0] + (iteration * rank)}
        x2={padding[3] + valueSpace}
        y2={padding[0] + (iteration * rank)}
        className="Graph-guide"
        stroke="#e6e6e6"
      />

    </g>
  );
}
