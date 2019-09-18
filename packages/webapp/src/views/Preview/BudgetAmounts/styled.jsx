import styled, { createGlobalStyle } from 'styled-components';
import { Typography } from '@material-ui/core';

const Wrapper = styled.div`
  font-family: Roboto;
  justify-content: center;
  margin-right: 16px;
  margin-left: 16px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }
`;

const Summary = styled.div`
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  margin: 0 auto;
  width: 100%;
  max-width: 1200px;
`;

const Numbers = styled.div`
  display: flex;
  padding-bottom: 36px;

  @media screen and (min-width: 600px) {
    padding-bottom: 64px;
  }
`;

const Budget = styled.div`
  width: 50%;
`;

const IntroMainHeading = styled(Typography)`
  && {
    font-size: 24px;
    line-height: 1.3;
    margin: 0;
    display: flex;
    align-items: center;
    color: #000;
    font-weight: 700;

    @media screen and (min-width: 600px) {
      font-size: 48px;
    }
  }
`;

const IntroSubHeading = styled(Typography)`
  && {
    font-size: 10px;
    margin: 0;
    color: #000;
    white-space: nowrap;

    @media screen and (min-width: 600px) {
      font-size: 20px;
    }
  }
`;

const Percentages = styled.div`
  display: flex;
  justify-content: flex-end;
  width: 66%;
  @media screen and (min-width: 600px) {
    width: 50%;
  }
`;

const TooltipStyled = createGlobalStyle`
  .previewPercentageTooltip {
    text-align: center;
  }
`;

export {
  Wrapper,
  Summary,
  Numbers,
  Budget,
  IntroMainHeading,
  IntroSubHeading,
  Percentages,
  TooltipStyled,
};

export default {
  Wrapper,
  Summary,
  Numbers,
  Budget,
  TooltipStyled,
};
