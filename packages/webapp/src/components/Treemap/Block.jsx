import React, { Fragment } from 'react';
import { lighten } from 'polished';
import { Tooltip } from '@material-ui/core';

import CustomIcon from '../CustomIcon';

import {
  Text,
  TextContainer,
  TreemapBlock,
  TreemapBlockWrapper,
  BlockContent,
  ResetTooltipDefaultStyling,
} from './styled';
import TooltipContent from './TooltipContent';
import trimValues from '../../helpers/trimValues';

const createIcon = icon => (
  <div
    style={{
      background: 'black',
      width: '32px',
      height: '32px',
      borderRadius: '50%',
      color: 'white',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    }}
  >
    <CustomIcon type={icon} fontSize="small" />
  </div>
);

const createInlineText = (title, amount, squarePixels, icon) => (
  <Fragment>
    {!!icon && squarePixels > 20000 && createIcon(icon)}
    <TextContainer>
      <Text bold small={squarePixels < 20000}>
        {squarePixels < 8000 && title.length > 15 ? `${title.substring(0, 15)}...` : title}
      </Text>
      <Text small={squarePixels < 20000}>R{trimValues(amount, true)}</Text>
    </TextContainer>
  </Fragment>
);

const Block = props => {
  const {
    depth,
    x,
    y,
    id,
    url,
    width,
    height,
    color,
    selected,
    name,
    amount,
    changeSelectedHandler,
    children,
    root,
    zoom,
    icon,
  } = props;

  if (depth === 2) {
    const { name: rootName } = root;
    const fullName = `${rootName}: ${name}`;

    return (
      <TreemapBlockWrapper {...{ x, y, width, height }} key={id}>
        <div style={{ border: `1px solid ${lighten(0.1, color)}` }}>
          <ResetTooltipDefaultStyling />
          <Tooltip
            title={<TooltipContent {...{ amount }} name={fullName} />}
            placement="top"
            classes={{ tooltip: 'treemapBlockTooltipOverride' }}
          >
            <BlockContent>
              <TreemapBlock
                onClick={() =>
                  changeSelectedHandler({
                    id,
                    name: fullName,
                    color,
                    value: amount,
                    url,
                    zoom: rootName,
                  })
                }
              />
            </BlockContent>
          </Tooltip>
        </div>
      </TreemapBlockWrapper>
    );
  }

  if (depth !== 1) {
    return null;
  }

  const squarePixels = width * height;

  return (
    <TreemapBlockWrapper x={x} y={y} width={width} height={height} key={id}>
      <ResetTooltipDefaultStyling />
      <Tooltip
        title={<TooltipContent {...{ amount, name }} />}
        placement="top"
        classes={{ tooltip: 'treemapBlockTooltipOverride' }}
      >
        <BlockContent>
          <TreemapBlock
            {...{ color, zoom }}
            selected={!children && selected && selected === id}
            onClick={() => changeSelectedHandler({ id, name, color, value: amount, url, zoom })}
          >
            {width > 60 &&
              squarePixels > 6000 &&
              createInlineText(name, amount, squarePixels, icon)}
          </TreemapBlock>
        </BlockContent>
      </Tooltip>
    </TreemapBlockWrapper>
  );
};

export default Block;
