import React from 'react';

import Icon from '@material-ui/icons/ArrowForward';
import CssBaseline from '@material-ui/core/CssBaseline';
import trimValues from '../../helpers/trimValues';
import SectionHeading from '../SectionHeading';

import {
  Wrapper,
  DetailsWrapper,
  LinkWrapper,
  ButtonStyle,
  TextExploreButton,
  SpanStyled,
  DetailsContainer,
  Department,
  Amount,
  ChartWrapper,
  ChartContainer,
  FooterWrapper,
  FooterContainer,
  FooterDetails,
} from './styled';

const callChart = (chart, onSelectedChange) => (
  <ChartWrapper>
    <ChartContainer>{chart(onSelectedChange)}</ChartContainer>
  </ChartWrapper>
);

const callButtonExplore = (url, color, verb, subject) => {
  return (
    <LinkWrapper href={url}>
      <ButtonStyle disabled={!url} {...{ color }}>
        <TextExploreButton>
          {verb} <SpanStyled>{subject}</SpanStyled>
        </TextExploreButton>
        <Icon />
      </ButtonStyle>
    </LinkWrapper>
  );
};

const callDetails = (selected, verb, subject) => {
  const { name, value, url, color } = selected;
  if (value === null) {
    return null;
  }
  return (
    <DetailsWrapper>
      <DetailsContainer>
        <div>
          <Department>{name}</Department>
          <Amount>R{trimValues(value)}</Amount>
        </div>
        {!!verb && callButtonExplore(url, color, verb, subject)}
      </DetailsContainer>
    </DetailsWrapper>
  );
};

const Markup = props => {
  const {
    chart,
    selected,
    onSelectedChange,
    verb,
    subject,
    footer,
    years,
    phases,
    anchor,
    title,
  } = props;

  return (
    <Wrapper>
      <CssBaseline />
      <SectionHeading title={title} share={anchor} years={years} phases={phases} />
      {!!selected && callDetails(selected, verb, subject)}
      {callChart(chart, onSelectedChange)}
      <FooterWrapper>
        <FooterContainer>{footer && <FooterDetails>{footer}</FooterDetails>}</FooterContainer>
      </FooterWrapper>
    </Wrapper>
  );
};

export default Markup;
