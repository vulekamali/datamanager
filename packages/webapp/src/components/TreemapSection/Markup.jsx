import React from 'react';
import trimValues from '../../helpers/trimValues';
import Icon from '@material-ui/icons/ArrowForward';
import SpeedDial from '../SpeedDial';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';

import {
  Wrapper,
  TreemapWrapper,
  BudgetContainer,
  BudgetHeading,
  IconAndDates,
  DateButton,
  DetailsContainer,
  Department,
  Amount,
  PhaseContainer,
  BudgetPhaseButton,
  LinkWrapper,
  ButtonStyle,
  FooterContainer,
  FooterDetails,
  NoticeMessage,
  TreemapContainer,
  ZoomButtonContainer,
  ZoomButton
 } from './styled';
import GlobalStyle from './GlobalStyle';
import styled from "styled-components";


const TreemapContained = styled.div`
  height: 500px;
`;

const ZoomLevelIndicator = styled.p`
  font-family: Roboto, sans-serif;
  font-size: 12px;
`;

const callButtonExplore = (selected) => (
  <LinkWrapper href={selected.detail}>
    <ButtonStyle {...{selected}}>
      <span>Explore this department</span>
      <Icon />
    </ButtonStyle>
  </LinkWrapper>
);

const callTreeMap = (eventZoomIn, eventZoomOut, selected, latestBudget, totalBudget,
                     zoomOutButtonState, zoomInButtonState, nextBiggestObjectOutsideView) => {
  return (
    <React.Fragment>
      <DetailsContainer>
        <div>
          <Department>{selected ? selected.name : `National departments budget`}</Department>
          <Amount>R{selected ? trimValues(selected.amount) : trimValues(totalBudget)}</Amount>
          <PhaseContainer>
            <BudgetPhaseButton>Original Budget</BudgetPhaseButton>
          </PhaseContainer>
        </div>
        {selected ? callButtonExplore(selected) : null}
      </DetailsContainer>
      <ZoomLevelIndicator>
        {nextBiggestObjectOutsideView ? 'Showing departments smaller than: ' + nextBiggestObjectOutsideView.name + ' (R' + trimValues(nextBiggestObjectOutsideView.amount) + ')' : ``}
      </ZoomLevelIndicator>
      <TreemapContainer>
        <React.Fragment>
        <GlobalStyle />
        <TreemapContained id="treemap" />
      </React.Fragment>
          <ZoomButtonContainer>
          <ZoomButton disabled={zoomOutButtonState} onClick={eventZoomOut}>
            <RemoveIcon />
          </ZoomButton>
          <ZoomButton disabled={zoomInButtonState} onClick={eventZoomIn}>
            <AddIcon />
          </ZoomButton>
        </ZoomButtonContainer>
      </TreemapContainer>
      <FooterContainer>
        <FooterDetails>Budget data from 1 April 2019 - 31 March 2020</FooterDetails>
        <FooterDetails>Direct charges against the National Revenue Fund are excluded</FooterDetails>
      </FooterContainer>
    </React.Fragment>
  );
};

const callNotice = () => (
  <React.Fragment>
    <NoticeMessage>The data for the provincial budget summary will be available in April.</NoticeMessage>
  </React.Fragment>
);


const Markup = (props) => {

  const {
    eventZoomIn,
    eventZoomOut,
    selected,
    latestBudget,
    totalBudget,
    isNationalBudget,
    zoomOutButtonState,
    zoomInButtonState,
    nextBiggestObjectOutsideView,
  } = props;

  return (
    <Wrapper>
      <TreemapWrapper>
        <BudgetContainer>
          <BudgetHeading>{isNationalBudget ? `National Budget Summary` : `Provincial Budget Summary`}</BudgetHeading>
          <IconAndDates>
            <SpeedDial />
            <div>
              <DateButton>2019-20</DateButton>
            </div>
          </IconAndDates>
        </BudgetContainer>
        {isNationalBudget ? callTreeMap(eventZoomIn, eventZoomOut, selected, latestBudget, totalBudget,
            zoomOutButtonState, zoomInButtonState, nextBiggestObjectOutsideView) : callNotice()}
      </TreemapWrapper>
    </Wrapper>
  );
};

export default Markup;
