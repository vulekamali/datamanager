import LabelItem from './LabelItem.jsx';


export default function Labels({ totalGroupSpace, groupSpaceArray, items, styling }) {
  const titles = Object.keys(items);
  const { padding, buffer, valueSpace, maxValue } = styling;

  return (
    <g className="Graph-horisontalLabelList">
      {/* <rect
        y={285}
        x={padding[3]}
        width={valueSpace}
        height={padding[2]}
        fill="red"
        opacity="0.5"
      /> */}

      {
        titles.map((title, index) => {
          return (
            <LabelItem
              rank={index}
              {...{ title, totalGroupSpace, groupSpaceArray, styling }}
            />
          );
        })
      }
    </g>
  );
}
