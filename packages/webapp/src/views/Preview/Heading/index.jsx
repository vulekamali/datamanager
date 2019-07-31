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
  RightOptions,
  Link,
  ButtonDetails,
  ButtonText,
  ArrowStyled,
  Details,
  DetailedAnalysis
 } from './styled';

const Heading = ({ government, departmentNames, selected, eventHandler, year, sphere }) => {
  const provinceFolder = government === 'south-africa' ? '' : `${government}/`;
  const url = `/${year}/${sphere}/${provinceFolder}departments/${selected}`;

  return (
    <HeadingWrapper>
      <HeadingContainer>
        <HeadingText>
          <Title>{calcPrettyName(government)}</Title>
        </HeadingText>
        <SelectsGroup>
          <CustomizedSelect {...{ departmentNames, selected, eventHandler }} />
          <RightOptions>
            <CustomizedDateSelect />
            <Link href={url}>
            <ButtonDetails>
              <ButtonText><Details>Details</Details><DetailedAnalysis>Detailed Analysis</DetailedAnalysis></ButtonText>
              <ArrowStyled />
            </ButtonDetails>
            </Link>
          </RightOptions>
        </SelectsGroup>
      </HeadingContainer>
    </HeadingWrapper>
  )
};


export default Heading;
