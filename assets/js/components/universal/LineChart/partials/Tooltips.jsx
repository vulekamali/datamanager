import { h } from 'preact';
import TooltipGroup from './TooltipGroup.jsx';


export default function Tooltips({ totalGroupSpace, groupSpaceArray, items, styling }) {
  const titles = Object.keys(items);
  const { padding, buffer, valueSpace } = styling;

  return (
    <g className="LineGroupList">
      {/* <rect
        x={padding[3] + buffer}
        y="0"
        width={valueSpace - buffer}
        height={totalGroupSpace + padding[0]}
        fill="red"
        opacity="0.5"
      /> */}

      {
        titles.map((key, index) => {
          return (
            <TooltipGroup
              rank={index}
              lines={items[key]}
              title={key}
              {...{ totalGroupSpace, groupSpaceArray, styling }}
            />
          );
        })
      }
    </g>
  );
}
