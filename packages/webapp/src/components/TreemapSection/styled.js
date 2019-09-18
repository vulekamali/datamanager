import { Typography, Button } from '@material-ui/core';
import styled from 'styled-components';
import { darken } from 'polished';

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 40px 20px;

  @media screen and (min-width: 450px) {
    margin: 70px 20px;
  }
`;

const TreemapWrapper = styled.div`
  width: 100%;
  max-width: 1000px;
`;

const BudgetContainer = styled.div`
  border-bottom: 1px solid #000;
  margin-bottom: 20px;
  width: 100%;

  @media screen and (min-width: 450px) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
`;

const BudgetHeading = styled(Typography)`

  &&&& {
    font-weight: 700;
    font-size: 20px;
    line-height: 24px;
    color: #000;
    text-transform: Capitalize;
    width: 100%;
    padding-bottom: 20px;
    text-align: center;

    @media screen and (min-width: 450px) {
      font-size: 24px;
      border-right: 1px solid #000;
      font-size: 32px;
      line-height: 65px;
      text-align: left;
      padding-bottom: 0;
    }
  }
`;

const IconAndDates = styled.div`
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;

  @media screen and (min-width: 450px) {
    padding-left: 30px;
    padding-bottom: 0;
  }
`;

const DateButton = styled.div`

  && {
    font-family: Roboto;
    font-weight: 700;
    font-size: 16px;
    line-height: 24px;
    text-align: center;
    letter-spacing: 0.15px;
    color: #000;

    @media screen and (min-width: 450px) {
      font-size: 24px;
      padding-right: 20px;
      padding-left: 20px;
    }
  }
`;

const DetailsContainer = styled.div`
  padding-bottom: 10px;

  @media screen and (min-width: 450px) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 35px;
  }
`;

const Department = styled(Typography)`

  && {
    font-size: 20px;
    line-height: 20px;
    color: #000;
    text-transform: Capitalize;

    @media screen and (min-width: 450px) {
      font-size: 24px;
      line-height: 65px;
    }
  }
`;

const Amount = styled(Typography)`

  && {
    font-size: 24px;
    font-weight: 700;
    line-height: 20px;
    color: #000;

    @media screen and (min-width: 450px) {
      font-size: 50px;
      line-height: 65px;
    }
  }
`;

const PhaseContainer = styled.div`
  margin-top: 20px;
`;

const BudgetPhaseButton = styled.div`

  && {
    font-family: Roboto;
    font-size: 16px;
    font-weight: 700;
    line-height: 24px;
    text-align: left;
    letter-spacing: 0.15px;
    color: #000;

    @media screen and (min-width: 450px) {
      font-size: 24px;
    }
  }
`;

const LinkWrapper = styled.a`
  text-decoration: none;
`;

const ButtonStyle = styled(Button)`
  width: 295px;

  && {
    background-color: ${({ selected }) => (selected ? selected.color : null)};
    text-transform: none;
    box-shadow: none;
    min-width: 0;
    font-weight: 700;
    font-size: 16px;
    line-height: 30px;
    text-align: center;
    color: #000;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;

    &:hover {
      background-color: ${({ selected }) => darken(0.1, selected.color)};
    }

    @media screen and (min-width: 450px) {
      font-size: 20px;
      line-height: 65px;
      padding-right: 20px;
      padding-left: 20px;
      margin-top: none;
    }
  }
`;

const FooterContainer = styled.div`
  margin-top: 10px;

  @media screen and (min-width: 450px) {
    margin-top: 25px;
  }
`;

const FooterDetails = styled(Typography)`

  && {
    font-size: 12px;
    line-height: 24px;
    color: #000;
    text-align: center;

    @media screen and (min-width: 450px) {
      text-align: left;
    }
  }
`;

const NoticeMessage = styled(Typography)`

  && {
    font-weight: 700;
    font-size: 18px;
    line-height: 65px;
    color: #666;
    text-transform: Uppercase;
    text-align: center;
  }
`;

const TreemapContainer = styled.div`
  position: relative;
`;

const ZoomButtonContainer = styled.div`
  position: absolute;
  bottom: 5px;
  right: 5px;
  height: 85px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  @media screen and (min-width: 450px) {
      flex-direction: row;
      width: 85px;
      height: 40px;
    }
`;

const ZoomButton = styled(Button)`
  && {
    background-color: #DCDCDC;
    padding: 0;
    min-width: 0;
    width: 40px;
    height: 40px;

    &:hover {
      background-color: ${darken(0.1, '#DCDCDC')};
    }
  }
`;

export {
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
}

export default {
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
}
