import breakIntoWrap from './../partials/breakIntoWrap.js';

export default function Heading({ heading, subHeading, type, left }) {
  const titleArray = breakIntoWrap(heading, 33);

  return (
    <g>
      <text y="49" x={left} font-size="28" font-weight="bold" fill="#3f3f3f" font-family="sans-serif">
        {
          titleArray.map((text, index) => <tspan x={left} y={49 + (30 * index)}>{text.trim()}</tspan>)
        }
      </text>
      <text y={42 + (30 * titleArray.length)} x={left} font-size="14" font-weight="bold" fill="#808080" font-family="sans-serif">{ subHeading }</text>
      <text y={62 + (30 * titleArray.length)} x={left} font-size="14" font-weight="bold" fill="#79b43c" font-family="sans-serif">{ type }</text>
    </g>
  );
}
