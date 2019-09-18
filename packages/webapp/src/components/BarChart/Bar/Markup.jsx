import React from 'react';

import trimValues from '../../../helpers/trimValues'

import {
  BarChartTotal,
  ColorBar,
  Title,
  Amount,
  Details
 } from './styled';

const createlabel = (title, amount, textNode, labelOutside) => (
  <Details ref={textNode} {...{ labelOutside }}>
    <Title component='div'>{title}</Title>
    <Amount component='div'>{`R${trimValues(amount)}`}</Amount>
  </Details>
);

const callColorBar = (ratio, title, amount, textNode, componentNode, labelOutside, fills, index) => {
  const color = fills[index];

  if (labelOutside) {
    return (
      <React.Fragment>
        <ColorBar ref={componentNode} {...{ ratio, color }} />
        {createlabel(title, amount, textNode, labelOutside)}
      </React.Fragment>
    );
  }
  return (
    <ColorBar ref={componentNode} {...{ ratio, color }}>
      {createlabel(title, amount, textNode)}
    </ColorBar>
  );
};

const Bar = props => {
  const {
    ratio,
    title,
    amount,
    labelOutside,
    textNode,
    componentNode,
    fills,
    index
  } = props;

  return (
    <BarChartTotal>
      {callColorBar(ratio, title, amount, textNode, componentNode, labelOutside, fills, index)}
    </BarChartTotal>
  )
};

export default Bar;
