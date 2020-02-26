import React from 'react';

import calcPrettyName from './calcPrettyName';

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
  DetailedAnalysis,
  DataYear,
 } from './styled';

const Heading = ({ government, departmentNames, selected, eventHandler, financialYearSlug, sphere }) => {
  const provinceFolder = government === 'south-africa' ? '' : `${government}/`;
  const url = `/${financialYearSlug}/${sphere}/${provinceFolder}departments/${selected}`;

  return (
    <HeadingWrapper>
      <HeadingContainer>
        <HeadingText>
          <Title>{calcPrettyName(government)}</Title>
        </HeadingText>
        <SelectsGroup>
          <CustomizedSelect {...{ departmentNames, selected, eventHandler }} />
          <RightOptions>
            <DataYear>{ financialYearSlug }</DataYear>
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
