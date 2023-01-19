import trimValues from './../../../../utilities/js/helpers/trimValues.js';


export default function TooltipItem({ styling, xTriggerPosition, xPosition, yPosition, amount, colour, totalGroupSpace }) {
  const { barWidth, lineGutter, padding, popupWidth, popupHeight, buffer, svgHeight, popupFontSize } = styling;

  // const { popUpOffset } = styling;

  return (
    <g className="ColumnChart-tooltip">

      {/* <rect
        x={xPosition - (popupWidth / 2)}
        y={yPosition + barWidth}
        width={popupWidth}
        height={popupHeight + popUpOffset}
        fill="blue"
        opacity="0.5"
      /> */}

      {/* <rect
        x={xPosition - ((barWidth + lineGutter) / 2)}
        y={0}
        width={barWidth + lineGutter}
        height={totalGroupSpace + padding[0]}
        fill="none"
        stroke="blue"
        opacity="0.5"
      /> */}

      <rect
        x={xPosition - ((barWidth + lineGutter) / 2)}
        x1={xTriggerPosition}
        y={0}
        width={barWidth + lineGutter}
        height={svgHeight + padding[0] + buffer}
        opacity="0"
      />

      <rect
        rx="10"
        ry="10"
        className="Graph-tooltipBase"
        x={xPosition - (popupWidth / 2)}
        y={yPosition}
        width={popupWidth}
        height={popupHeight}
        fill={colour}
      />

      <polygon
        className="Graph-triangle"
        points={`
          ${xPosition},
          ${yPosition + barWidth + popupHeight}
          ${xPosition + (barWidth / 2)},
          ${yPosition + popupHeight}
          
          ${xPosition - (barWidth / 2)},
          ${yPosition + popupHeight}
        `}
        fill={colour}
      />

      <text
        x={xPosition}
        y={(yPosition + (popupHeight / 2) + (popupFontSize / 2)) - 2}
        font-size={popupFontSize}
        className="Graph-tooltipText"
        font-family="sans-serif"
        text-anchor="middle"
        fill="white"
      >
        {trimValues(amount)}
      </text>
    </g>
  );
}
