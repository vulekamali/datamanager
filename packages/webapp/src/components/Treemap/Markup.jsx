import React from 'react';
import { Treemap, Tooltip } from 'recharts';
import LeftIcon from '@material-ui/icons/ArrowBack';

import Block from './Block';
import IEBlock from './IEBlock';
import TooltipContent from './TooltipContent';
import calcIfForeignObjectIsSupported from './calcIfForeignObjectIsSupported';

import { TreemapWrapper, TreemapButtonStyle, TreemapButtonText } from './styled';

const createBlock = (fills, changeSelectedHandler, selected, zoom, icons) => props => {
  const passedProps = { ...props, fills, changeSelectedHandler, selected, zoom, icons };
  if (calcIfForeignObjectIsSupported()) {
    return <Block {...passedProps} />;
  } else {
    console.log("Using non-foreignObject treemap");
    return <IEBlock {...passedProps} />;
  }
};

const Markup = ({
  items,
  changeSelectedHandler,
  selected,
  fills,
  screenWidth,
  zoom,
  hasChildren,
  unsetZoomHandler,
}) => {
  const widthWithPadding = screenWidth - 48;
  const width = widthWithPadding > 1200 ? 1200 : widthWithPadding;

  const createButton = () => (
    <TreemapButtonStyle onClick={unsetZoomHandler}>
      <LeftIcon />
      <TreemapButtonText component="span">Provinces</TreemapButtonText>
    </TreemapButtonStyle>
  );

  return (
    <TreemapWrapper {...{ width }}>
      <Treemap
        {...{ width }}
        key={width}
        height={650}
        data={items}
        dataKey="amount"
        animationDuration={600}
        tooltip
        isAnimationActive={false}
        content={createBlock(fills, changeSelectedHandler, selected, zoom, hasChildren)}
      />
      {!!zoom && createButton()}
    </TreemapWrapper>
  );
};

export default Markup;
