

export default function HorisontalGuide({ styling, totalGroupSpace, rank }) {
  const { valueSpace, buffer, fontSize, padding, labelBreakpoints } = styling;
  const iteration = valueSpace / (labelBreakpoints - 1);

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
        x1={padding[3] + (iteration * rank) + iteration}
        y1={padding[0]}
        x2={padding[3] + (iteration * rank) + iteration}
        y2={padding[0] + totalGroupSpace + buffer}
        className="Graph-guide"
        stroke="#e6e6e6"
      />

    </g>
  );
}
