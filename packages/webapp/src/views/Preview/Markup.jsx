import React from 'react';
import ReactMarkdown from 'react-markdown';

import Heading from './Heading';
import BudgetAmounts from './BudgetAmounts';
import SectionHeading from './SectionHeading';
import BarChart from '../../components/BarChart';
import calcFineprint from './calcFineprint';

import {
  Wrapper,
  TextWrapper,
  TextContainer,
  Description,
  FooterWrapper,
  FooterContainer,
  FooterDetails,
  FocusWrapper,
  Link,
  ButtonStyled,
  TextButton,
  FocusLinksWrapper,
  FocusLinksContainer,
  ButtonContainer,
  ArrowStyled,
} from './styled';

const callDescription = description => {
  if (!description) {
    return null;
  }
  return (
    <React.Fragment>
      <SectionHeading title="Department information" />
      <TextWrapper>
        <TextContainer>
          <Description component="div">
            <ReactMarkdown source={description} />
          </Description>
        </TextContainer>
      </TextWrapper>
    </React.Fragment>
  );
};

const callFocusButtons = ({ slug, title, url }) => (
  <ButtonContainer key={slug}>
    <Link href={url}>
      <ButtonStyled>
        <TextButton component="div">{title}</TextButton>
        <ArrowStyled />
      </ButtonStyled>
    </Link>
  </ButtonContainer>
);

const callFocusAreas = focusAreas => (
  <FocusWrapper>
    <SectionHeading title="Focus areas of this department" />
    <FocusLinksWrapper>
      <FocusLinksContainer>{focusAreas.map(callFocusButtons)}</FocusLinksContainer>
    </FocusLinksWrapper>
  </FocusWrapper>
);

const Markup = props => {
  const {
    resources,
    items,
    description,
    sphere,
    government,
    departmentNames,
    selected,
    eventHandler,
    year,
    focusAreas,
  } = props;

  return (
    <Wrapper>
      <Heading {...{ departmentNames, government, selected, eventHandler, year, sphere }} />
      <BudgetAmounts {...resources} sphere={sphere} />
      {callDescription(description)}
      <SectionHeading title="Department programmes" />
      <div key={selected}>
        <BarChart {...{ items }} />
      </div>
      <FooterWrapper>
        <FooterContainer>
          <FooterDetails>{calcFineprint(year)}</FooterDetails>
          <FooterDetails>
            Direct charges against the national revenue fund included here, while it is not normally
            counted as part of the total budget of the department, as it is not part of the voted
            appropriation.
          </FooterDetails>
        </FooterContainer>
      </FooterWrapper>
      {focusAreas && callFocusAreas(focusAreas)}
    </Wrapper>
  );
};

export default Markup;
