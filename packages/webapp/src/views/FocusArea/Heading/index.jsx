import React from 'react';

import calcPrettyName from './calcPrettyName';

import CustomizedSelect from './CustomizedSelect';


import {
  HeadingWrapper,
  HeadingContainer,
  HeadingText,
  Title,
  SelectsGroup,
  RightOptions
 } from './styled';

const Heading = ({ government, departmentNames, selected, eventHandler, financialYearSlug, sphere }) => (
  <HeadingWrapper>
    <HeadingContainer>
      <HeadingText>
        <Title>{calcPrettyName(government)}</Title>
      </HeadingText>
      <SelectsGroup>
        <CustomizedSelect {...{ departmentNames, selected, eventHandler }} />
        <RightOptions>{financialYearSlug}</RightOptions>
      </SelectsGroup>
    </HeadingContainer>
  </HeadingWrapper>
);


export default Heading;
