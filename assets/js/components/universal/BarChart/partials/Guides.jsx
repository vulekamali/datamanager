import GuideItem from './GuideItem.jsx';


export default function Guides({ styling, totalGroupSpace }) {
  const { labelBreakpoints } = styling;

  let breakpointArray = [];

  for (let i = 0; i < labelBreakpoints; i++) {
    breakpointArray.push('');
  }

  // const { buffer, padding } = styling;

  return (
    <g className="Graph-verticalLabelList">
      {/* <rect
        x={padding[3] + buffer}
        y={padding[0]}
        height={totalGroupSpace}
        width={padding[3] - buffer}
        fill="red"
        opacity="0.5"
      /> */}

      {
        breakpointArray.map((val, index) => {
          if (index !== breakpointArray.length - 1) {
            return (
              <GuideItem rank={index} {...{ styling, totalGroupSpace }} />
            );
          }

          return null;
        })
      }
    </g>
  );
}
