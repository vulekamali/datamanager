import styled from 'styled-components';
import { Typography } from '@material-ui/core';

const BarChartTotal = styled.div`
  display: flex;
  width: 100%;
  height: 42px;
  margin-bottom: 8px;
  background-color: #f7f7f7;

  @media screen and (min-width: 600px) {
    height: 48px;
  }
`;

const ColorBar = styled.div`
  width: ${({ ratio }) => ratio}%;
  background-color: ${({ color }) => color};
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-end;
  white-space: nowrap;
`;

const Details = styled.div`
  text-align: ${({ labelOutside }) => (labelOutside ? 'left' : 'right')};
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-right: 12px;
  padding-left: 12px;

  @media screen and (min-width: 600px) {
    padding-right: 16px;
    padding-left: 16px;
  }
`;

const Title = styled(Typography)`
  && {
    font-weight: 700;
    font-size: 10px;
    line-height: 120%;
    color: #000;

    @media screen and (min-width: 600px) {
      font-size: 14px;
    }
  }
`;

const Amount = styled(Typography)`
  && {
    font-size: 10px;
    line-height: 120%;
    color: #000;

    @media screen and (min-width: 600px) {
      font-size: 14px;
      line-height: 100%;
    }
  }
`;

export {
  BarChartTotal,
  ColorBar,
  Title,
  Amount,
  Details
}

export default {
  BarChartTotal,
  ColorBar,
  Title,
  Amount,
  Details
}
