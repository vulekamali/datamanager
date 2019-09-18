import styled from 'styled-components';
import { Typography } from '@material-ui/core';

const Wrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }
`;

const BarChartContainer = styled.div`
  width: 100%;
  max-width: 1200px;
`;

const BarChartTotal = styled.div`
  display: flex;
  width: 100%;
  height: 75px;
  margin-bottom: 10px;
  background-color: #f7f7f7;
`;

const ColorBar = styled.div`
  width: ${({ ratio }) => ratio}%;
  background-color: #e57373;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-end;
  padding-right: 24px;
`;

const Title = styled(Typography)`
  && {
    font-weight: 700;
    font-size: 10px;
    line-height: 120%;
    text-align: right;
    color: #000;

    @media screen and (min-width: 600px) {
      font-size: 18px;
    }
  }
`;

const Amount = styled(Typography)`
  && {
    font-size: 10px;
    line-height: 120%;
    text-align: right;
    color: #000;

    @media screen and (min-width: 600px) {
      font-size: 18px;
    }
  }
`;

export {
  Wrapper,
  BarChartContainer,
  BarChartTotal,
  ColorBar,
  Title,
  Amount
}

export default {
  Wrapper,
  BarChartContainer,
  BarChartTotal,
  ColorBar,
  Title,
  Amount
}
