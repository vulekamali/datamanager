import { Typography, Button } from '@material-ui/core';
import styled from 'styled-components';
import { darken } from 'polished';
import removeProps from '../../helpers/removeProps';

const Wrapper = styled.div`
  margin-bottom: 60px;
`;

const LinkWrapper = styled.a`
  text-decoration: none;
`;

const ButtonStyle = styled(removeProps({ component: Button, blacklist: 'color' }))`
  && {
    background-color: ${({ color }) => color};
    text-transform: none;
    box-shadow: none;
    min-width: 0;
    font-weight: 700;
    font-size: 14px;
    line-height: 120%;
    text-align: center;
    color: #000;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 12px 12px 16px;

    &:hover {
      background-color: ${({ color }) => darken(0.1, color)};
    }

    @media screen and (min-width: 950px) {
      font-size: 20px;
      padding: 20px 24px;
    }
  }
`;

const TextExploreButton = styled.div`
  padding-right: 12px;
  white-space: nowrap;

  @media screen and (min-width: 450px) {
    padding-right: 24px;
  }
`;

const SpanStyled = styled.span`
  display: none;
  @media screen and (min-width: 950px) {
    display: inline-block;
  }
`;

const DetailsWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;
`;

const DetailsContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  padding-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  @media screen and (min-width: 950px) {
    padding-bottom: 32px;
  }
`;

const Department = styled(Typography)`
  && {
    font-size: 14px;
    font-weight: 700;
    line-height: 120%;
    color: #000;
    text-transform: Capitalize;

    @media screen and (min-width: 950px) {
      font-size: 20px;
    }
  }
`;

const Amount = styled(Typography)`
  && {
    font-size: 20px;
    font-weight: 700;
    line-height: 120%;
    color: #000;

    @media screen and (min-width: 950px) {
      font-size: 48px;
    }
  }
`;

const ChartWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;
`;

const ChartContainer = styled.div`
  width: 100%;
  max-width: 1200px;
`;

const FooterWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;
`;

const FooterContainer = styled.div`
  margin-top: 16px;
  width: 100%;
  max-width: 1200px;

  @media screen and (min-width: 950px) {
    margin-top: 32px;
  }
`;

const FooterDetails = styled.div`
  && {
    font-size: 10px;
    line-height: 140%;
    color: #000;
    text-align: left;
    font-family: Roboto;
  }

  @media screen and (min-width: 950px) {
    font-size: 12px;
  }
`;

export {
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
};

export default {
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
};
