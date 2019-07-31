import styled from 'styled-components';
import { darken } from 'polished';

import { Typography, Button } from '@material-ui/core';
import Arrow from '@material-ui/icons/ArrowForward';

const HeadingWrapper = styled.div`
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  background: #efefef;
  padding: 16px;
  margin-bottom: 36px;

  @media screen and (min-width: 600px) {
    padding: 64px 16px;
    margin-bottom: 64px;
  }
`;

const HeadingContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  box-sizing: border-box;
`;

const HeadingText = styled.div`
  width: 100%;
`;

const Title = styled(Typography)`
  && {
    font-size: 32px;
    font-weight: 700;
    line-height: 120%;
    color: #000;

    @media screen and (min-width: 600px) {
      font-size: 48px;
    }
  }
`;

const SelectsGroup = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;

  @media screen and (min-width: 1200px) {
    flex-direction: row;
    justify-content: space-between;
  }
`;

const RightOptions = styled.div`
  display: flex;
  justify-content: flex-start;
  width: 100%;

  @media screen and (min-width: 600px) {
    margin-top: 24px;
  }

  @media screen and (min-width: 1200px) {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
`;

const Link = styled.a`
  text-decoration: none;
`;

const ButtonDetails = styled(Button)`
  && {
    width: 100%;
    background: #000;
    color: #fff;
    text-transform: none;
    padding: 10px 13px 9px 16px;

    &:hover {
      background: ${darken(0.1, '#000')};
    }

    @media screen and (min-width: 600px) {
      padding: 20px 16px;
    }
  }
`;

const ButtonText = styled.span`
  font-family: Roboto;
  font-weight: 700;
  font-size: 14px;
  line-height: 120%;
  letter-spacing: 0.15px;
  white-space: nowrap;

  @media screen and (min-width: 600px) {
    font-size: 20px;
  }
`;

const Details = styled.span`
  font-family: Roboto;
  font-weight: 700;
  font-size: 14px;
  line-height: 120%;
  letter-spacing: 0.15px;
  white-space: nowrap;

  @media screen and (min-width: 600px) {
    display: none;
  }
`;
const DetailedAnalysis = styled.span`
  display: none;

  @media screen and (min-width: 600px) {
    display: block;
    font-family: Roboto;
    font-weight: 700;
    font-size: 20px;
    line-height: 120%;
    letter-spacing: 0.15px;
    white-space: nowrap;
  }
`;

const ArrowStyled = styled(Arrow)`
  && {
    padding-left: 13px;
    box-sizing: content-box;
  }
`;

export {
  HeadingWrapper,
  HeadingContainer,
  HeadingText,
  Title,
  SelectsGroup,
  RightOptions
}

export default {
  HeadingWrapper,
  HeadingContainer,
  HeadingText,
  Title,
  SelectsGroup,
  RightOptions
}
