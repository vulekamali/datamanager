import calcMaxValue from './partials/calcMaxValue.js';
import buildGroupSpaceArray from './partials/buildGroupSpaceArray.js';
import breakIntoWrap from './partials/breakIntoWrap.js';

import Breakpoints from './partials/Breakpoints.jsx';
import Grid from './partials/Grid.jsx';
import Guides from './partials/Guides.jsx';
import LineGroups from './partials/LineGroups.jsx';
import Tooltips from './partials/Tooltips.jsx';
import Attribution from './partials/Attribution.jsx';
import Heading from './partials/Heading.jsx';
import Logo from './partials/Logo.jsx';


export default function BarChart(props) {
  const {
    items,
    width,
    hover,
    guides,
    scale = 1,
    download,
    purple,
  } = props;

  const { getNode } = props;

  if (!width) {
    const loader = <div className="Loader u-marginTop50 u-marginLeftAuto u-marginRightAuto u-marginBottom40" />;

    return (
      <div className="LineChart" ref={node => getNode && getNode(node)}>
        {loader}
      </div>
    );
  }

  let content = null;

  let styling = {
    fontSize: 14,
    popupFontSize: 14,
    maxValue: calcMaxValue(items),
    popupWidth: 90,
    popUpOffset: 6,
    buffer: 20,
    padding: [0, 110, 60, 2],
    valueSpace: width - (112),
    lineGutter: 23,
    popupHeight: 30,
    popupCentre: 5,
    barWidth: 16,
    groupMargin: 60,
    charWrap: width / 10,
    charLineHeight: 16,
    titleSpace: 0,
    labelBreakpoints: Math.floor(width / 150),
    showGuides: true,
  };

  if (download) {
    const titleArray = breakIntoWrap(download.heading, 33);

    styling = {
      ...styling,
      padding: [83 + (30 * titleArray.length), 140, 137, 30],
      valueSpace: width - (140 + 30),
    };
  }

  if (width > 200) {
    const { valueSpace, padding, showGuides } = styling;
    const groupSpaceArray = buildGroupSpaceArray(items, styling);
    const totalGroupSpace = groupSpaceArray.reduce((result, val) => result + val, 0);
    const height = padding[0] + totalGroupSpace + padding[2];
    const newWidth = padding[3] + valueSpace + padding[1];

    const background = (
      <rect
        x="0"
        y="0"
        width={newWidth}
        height={height}
        fill="white"
      />
    );

    content = (
      <svg
        version="1.1"
        className={`BarChart-svg ${hover ? ' is-hoverable' : ''}`}
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${newWidth} ${height}`}
        width={newWidth * (scale || 1)}
        height={height * (scale || 1)}
        style={{ maxWidth: newWidth * (scale || 1) }}
      >

        {download ? background : null}

        { download ?
          <Heading
            left={padding[3]}
            heading={download.heading}
            subHeading={download.subHeading}
            type={download.type}
          /> :
          null
        }

        {width > 300 ? <Breakpoints {...{ styling, totalGroupSpace }} /> : null}
        <Grid {...{ styling, totalGroupSpace }} />
        {guides ? <Guides {...{ styling, totalGroupSpace }} /> : null}
        <LineGroups {...{ totalGroupSpace, groupSpaceArray, items, styling, purple }} />
        <Tooltips {...{ totalGroupSpace, groupSpaceArray, items, styling, purple }} />

        { download ?
          <g>
            <Logo top={((padding[0] + totalGroupSpace) / 2) + 17} left={padding[3]} />
            <Attribution top={padding[0] + totalGroupSpace + 90} left={padding[3] + valueSpace} />
          </g> :
          null
        }
      </svg>
    );
  }

  if (!download) {
    return (
      <div
        className="BarChart"
        ref={node => getNode && getNode(node)}
      >
        {content}
      </div>
    );
  }

  return content;
}
