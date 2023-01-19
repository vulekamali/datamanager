

export default function Grid({ styling, totalGroupSpace }) {
  const { padding, valueSpace, buffer } = styling;

  return (
    <g className="Graph-grid">

      {/* <rect
        x={padding[3]}
        y={padding[0]}
        width={valueSpace}
        height={totalGroupSpace + buffer}
        fill="red"
        opacity="0.5"
      /> */}

      <line
        className="Graph-outline"
        x1={padding[3]}
        y1={padding[0]}
        x2={padding[3]}
        y2={padding[0] + totalGroupSpace}
        stroke-width="2"
        stroke="#d2d2d2"
        fill="none"
      />

      <path
        className="Graph-outline"
        d={`
          M${padding[3]} ${padding[0] + totalGroupSpace} 
          Q ${padding[3]} ${padding[0] + buffer + totalGroupSpace}, 
          ${padding[3] + buffer} ${padding[0] + buffer + totalGroupSpace}
        `}
        stroke-width="2"
        stroke="#d2d2d2"
        fill="none"
      />

      <line
        className="Graph-outline"
        x1={padding[3] + buffer}
        y1={padding[0] + totalGroupSpace + buffer}
        x2={padding[3] + valueSpace}
        y2={padding[0] + totalGroupSpace + buffer}
        stroke-width="2"
        stroke="#d2d2d2"
        fill="none"
      />
    </g>
  );
}
