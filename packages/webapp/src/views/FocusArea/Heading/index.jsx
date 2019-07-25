import React from 'react';

import calcPrettyName from './calcPrettyName';

import CustomizedDateSelect from './CustomizedDateSelect';
import CustomizedSelect from './CustomizedSelect';


import {
  HeadingWrapper,
  HeadingContainer,
  HeadingText,
  Title,
  SelectsGroup,
  RightOptions
 } from './styled';

const Heading = ({ government, departmentNames, selected, eventHandler, year, sphere }) => (
  <HeadingWrapper>
    <HeadingContainer>
      <HeadingText>
        <Title>{calcPrettyName(government)}</Title>
      </HeadingText>
      <SelectsGroup>
        <CustomizedSelect {...{ departmentNames, selected, eventHandler }} />
        <RightOptions>
          <CustomizedDateSelect />
        </RightOptions>
      </SelectsGroup>
    </HeadingContainer>
  </HeadingWrapper>
);


export default Heading;
