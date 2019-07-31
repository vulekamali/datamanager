import React from 'react';
import posed, { PoseGroup } from 'react-pose';
import trimValues from '../../helpers/trimValues';
import styled from 'styled-components';
import NationalMap from '../../components/NationalMap';
import { Typography } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import ForwardArrow from '@material-ui/icons/ArrowForward';
import { darken } from 'polished';
import Progressbar from '../../components/Progressbar';



const AnimationWrapper = posed.div({
  enter: {
    opacity: 1,

  },
  exit: {
    opacity: 0,
  }
});

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-top: 16px;

  @media screen and (min-width: 950px) {
    flex-direction: row;
    justify-content: space-between;
    max-width: 1100px;
    margin: 0 auto;
    position: relative;
    padding-top: 64px;
  }
`;

const MapWrapper = styled.div`
  display: none;
    max-width: 1000px;

  @media screen and (min-width: 950px) {
    width: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 auto;
  }
`;

const MapSubHeading = styled.div`
  font-family: Lato;
  font-weight: 900;
  line-height: normal;
  font-size: 10px;
  text-align: center;
  letter-spacing: 0.5px
  text-transform: Uppercase;
  color: #AAAAAA;
  padding-bottom: 16px;
`;

const DataGroup = styled.div`
  // max-width: 272px;
  margin: 0 auto;
  font-family: Lato;
  padding: 0 40px 16px;

  @media screen and (min-width: 650px) {
    // max-width: 360px;
  }
`;

const SubHeading = styled.div`
  color: #79B443;
  font-weight: 900;
  line-height: 16px;
  font-size: 10px;
  text-align: center;
  letter-spacing: 3px;
  text-transform: Uppercase;
  padding-bottom: 8px;

  @media screen and (min-width: 650px) {
    font-weight: 700;
    line-height: normal;
    font-size: 14px;
    text-align: left;
  }
`;

const Heading = styled.div`
  // width: 1000px;
  font-weight: 700;
  line-height: normal;
  font-size: 22px;
  text-align: center;
  text-transform: Capitalize;
  // max-width: 272px;
  padding-bottom: 24px;

  @media screen and (min-width: 650px) {
    font-size: 32px;
    text-align: left;
    // max-width: 419px;
  }
`;

const Stage = styled.div`
  font-weight: 700;
  line-height: 16px;
  font-size: 10px;
  text-align: center;
  letter-spacing: 0.5px
  text-transform: Uppercase;
  color: rgba(0, 0, 0, 0.5);
  padding-bottom: 8px;

  @media screen and (min-width: 650px) {
    line-height: normal;
    text-align: left;
    font-weight: 900;
  }
`;

const ProgressBarContainer = styled.div`
  padding-bottom: 24px;
`;

const BudgetGroup = styled.div`
  display: flex;
  justify-content: space-between;
  padding-bottom: 24px;
`;

const BudgetCashflow = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;

  @media screen and (min-width: 650px) {
    align-items: flex-start;
  }
`;

const CashflowTitle = styled.div`
  font-weight: 700;
  line-height: normal;
  font-size: 10px;
  text-align: center;
  letter-spacing: 0.5px
  text-transform: Uppercase;
  color: #696969;
  padding-bottom: 8px;

  @media screen and (min-width: 650px) {
    text-align: left;
    font-weight: 900;
  }
`;

const Estimation = styled.div`
  font-weight: 700;
  line-height: normal;
  font-size: 18px;
  text-align: center;

  @media screen and (min-width: 650px) {
    font-size: 24px;
    text-align: left;
  }
`;

const Text = styled(Typography)`
  & {
    font-weight: normal;
    line-height: 30px;
    font-size: 14px;
    text-align: center;

    @media screen and (min-width: 650px) {
      line-height: 23px;
      font-size: 16px;
      text-align: left;
      padding-bottom: 32px;
    }
  }
`;

const StyledButton = styled(Button)`
  && {
    font-family: Lato;
    margin: 0 auto;
    min-width: 212px;
    border-radius: 30px;
    color: #fff;
    background-color: #79B443;
    font-size: 16px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-transform: none;
    margin-top: 24px;
    padding-right: 20px;
    padding-left: 20px;

    &:hover {
      background: ${darken(0.1, '#79B443')};
    }

    @media screen and (min-width: 650px) {
      margin: 0;
    }
  }
`;

const StyledLink = styled.a`
  text-decoration: none;
`;

const SideWrapper = styled.div`
  // width: 1000px;
  // max-width: 270px;
  margin: 0 auto;
  font-family: Lato; 
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 40px 48px;
  // border-bottom: 1px solid #000;

  @media screen and (min-width: 650px) {
    // max-width: 419px;
    align-items: flex-start;
  }

  @media screen and (min-width: 950px) {
    // max-width: 300px;
    border-bottom: none;
    margin: 0;
    ${'' /* align-items: flex-start; */}
    padding-left: 40px;
  }
`; 

const SideSection = styled.div`
   padding-bottom: 25px;
`;

const SideTitle = styled.div`
   font-weight: 900;
   font-size: 10px;
   line-height: 16px;
   text-align: center;
   letter-spacing: 0.5px;
   text-transform: uppercase;
   color: rgba(0, 0, 0, 0.5);
   padding-bottom: 8px;

  @media screen and (min-width: 650px) {
    text-align: left;
    max-width: 419px;
  }

  @media screen and (min-width: 950px) {
    max-width: none;
  }
`;

const SideType = styled.div`
   line-height: 20px;
   font-size: 14px;
   text-align: center;
   text-transform: Capitalize;
   color: #000;

  @media screen and (min-width: 650px) {
    text-align: left;
    line-height: 16px;
    font-size: 16px;
    max-width: 419px;
  }

  @media screen and (min-width: 950px) {
    max-width: none;
  }
`;

const SideLink = styled.a`
  text-decoration: none;
  margin-bottom: 8px;
`;

const SideButton = styled(Button)`
  && {
    font-family: Lato;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    text-transform: none;
    // width: 270px;
    margin: 0 auto;
    font-family: Lato;
    font-size: 12px;
    line-height: 17px;
    letter-spacing: 0.1px;
    font-weight: normal;
    color: #000;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-right: 16px;
    padding-left: 16px;
    width: 100%;

    &:hover {
      background: rgba(0, 0, 0, 0.2);
    }

    @media screen and (min-width: 650px) {
      max-width: 419px;
    }

    @media screen and (min-width: 950px) {
      max-width: 190px;
    }
  }
`;

const SideMapButtonWrapper = styled.div`
  display: flex;
  justify-content: center;

  @media screen and (min-width: 650px) {
    width: 419px;
  }

  @media screen and (min-width: 950px) {
    width: 300px;
    position: absolute;
    top: 320px;
    left: 0;
    margin: 0 auto;
  }
`;

const SideButtonToMaps = styled(Button)`
  && {
    font-family: Lato;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    text-transform: none;
    width: 270px;
    margin: 0 auto;
    font-family: Lato;
    font-size: 12px;
    line-height: 17px;
    letter-spacing: 0.1px;
    font-weight: normal;
    color: #000;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-right: 16px;
    padding-left: 16px;

    &:hover {
      background: rgba(0, 0, 0, 0.2);
    }

    @media screen and (min-width: 650px) {
      width: 419px;
    }

    @media screen and (min-width: 950px) {
      width: 270px;;
    }
  }
`;


const createSideRender = (id, props) => {
  const {
    investment,
    infrastructure,
    department,
  } = props;

  return (
    <SideWrapper key={id}>
      <SideSection>
        <SideTitle>Nature of investment:</SideTitle>
        <SideType>{investment}</SideType>
      </SideSection>
      <SideSection>
        <SideTitle>Infrastructure type:</SideTitle>
        <SideType>{infrastructure}</SideType>
      </SideSection>
      <SideSection>
        <SideTitle>Department</SideTitle>
        <SideType>{department.name}</SideType>
      </SideSection>
      <SideLink href={department.url} style={{ marginRight: '20px' }}>
        <SideButton>
          <span>Explore this department</span>
          <ForwardArrow />
        </SideButton>
      </SideLink>
      {/* <SideMapButtonWrapper>
        <SideLink href='#'>
          <SideButtonToMaps>
            <span>View project on Google Maps</span>
            <ForwardArrow />
          </SideButtonToMaps>
        </SideLink>
      </SideMapButtonWrapper> */}
    </SideWrapper>
  );
}

const createItem = (props) => {
  const {
    subheading,
    heading,
    stage,
    totalBudget,
    projectedBudget,
    description,
    id,
    link,
    details
  } = props;


  return (
    <AnimationWrapper key={id} style={{ width: '100%' }}>
      <DataGroup>
        <SubHeading >{subheading}</SubHeading>
        <Heading>{heading}</Heading>
        <Stage>Project stage: {stage}</Stage>
          <ProgressBarContainer>
            <Progressbar stage={stage} />
          </ProgressBarContainer>
        <BudgetGroup>
          <BudgetCashflow>
            <CashflowTitle>Total budget:</CashflowTitle>
            <Estimation>{`R${trimValues(totalBudget)}`}</Estimation>
          </BudgetCashflow>
          <BudgetCashflow>
            <CashflowTitle>3 Years project budget:</CashflowTitle>
            <Estimation>{`R${trimValues(projectedBudget)}`}</Estimation>
          </BudgetCashflow>
        </BudgetGroup>
        <Text>{description}</Text>
        {!details && (
          <StyledLink href={link}>
            <StyledButton>
              <span>View in more detail</span>
              <ForwardArrow />
            </StyledButton>
          </StyledLink>
        )}
      </DataGroup>
    </AnimationWrapper>
  );
}

const createMap = (props, selected) => {
  const {
    details,
    points,
    activeProvinces: rawProvinces,
    id,
  } = props;

  const all = [
    "Eastern Cape",
    "Free State",
    "Gauteng",
    "Limpopo",
    "Mpumalanga",
    "KwaZulu-Natal",
    "Northern Cape",
    "Western Cape",
    "North West"
  ];

  const activeProvinces = rawProvinces.length > 0 ? rawProvinces : all;

  return (
    <MapWrapper key={JSON.stringify(points)}>
      {/* <MapSubHeading>Select a project on the map</MapSubHeading> */}
      <NationalMap size={!!details ? "medium" : "large"} {...{ points, activeProvinces }} selected={selected.points && selected.points[0].id} />
    </MapWrapper>
  );
}

const LeftWrap = styled.div`
display: none;
width: 100%;

@media screen and (min-width: 1070px) {
  display: block;
  // padding-right: 30px;
}
`;


const RightWrap = styled.div`
width: 100%;
// display: none;

@media screen and (min-width: 950px) {
  // padding-left: 60px;
}
`;


const Preview = (props) => {
  const {
    id,
    sideInfo,
    details,
    selected,
  } = props;

  return (
    <Wrapper>
      <LeftWrap>
        {createMap(props, selected)}
      </LeftWrap>
      <PoseGroup style={{ width: '100%' }}>
        {createItem(props)}
      </PoseGroup>
        {!!details && <RightWrap>{createSideRender(id, sideInfo)}</RightWrap>}
    </Wrapper>
  );
}

export default Preview;
