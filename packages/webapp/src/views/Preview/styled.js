import styled from 'styled-components';

import { Typography, Button } from '@material-ui/core';
import Arrow from '@material-ui/icons/ArrowForward';

const Wrapper = styled.div`
  background: #fff;
`;

const TextWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }
`;

const TextContainer = styled.div`
  margin-bottom: 32px;
  max-width: 1200px;
  width: 100%;

  @media screen and (min-width: 600px) {
    margin-bottom: 48px;
  }
`;

const Description = styled(Typography)`
  && {
    font-size: 14px;
    line-height: 26px;
    color: #000;

    & > h2 {
      margin-top: 0;
      font-size: 16px;
    }

    @media screen and (min-width: 600px) {
      font-size: 16px;
    }

    @media screen and (min-width: 850px) {
      font-size: 16px;
      columns: 2;
      column-gap: 60px;

      & > p {
        margin-top: 0;
      }
    }
  }
`;

const FooterWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }
`;

const FooterContainer = styled.div`
  margin-top: 8px;
  width: 100%;
  max-width: 1200px;

  @media screen and (min-width: 600px) {
    margin-bottom: 16px;
  }
`;

const FooterDetails = styled(Typography)`
  && {
    font-size: 10px;
    line-height: 140%;
    color: #000;
    text-align: left;

    @media screen and (min-width: 600px) {
      font-size: 12px;
    }
  }
`;

const FocusWrapper = styled.div`
  margin-top: 48px;
`;

const FocusLinksWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }
`;

const FocusLinksContainer = styled.div`
  margin-top: 8px;
  width: 100%;
  max-width: 1200px;

  @media screen and (min-width: 600px) {
    margin-bottom: 16px;
    display: flex;
    flex-wrap: wrap;
  }
`;

const ButtonContainer = styled.div`
  margin-bottom: 16px;
  margin-right: 16px;
`;

const Link = styled.a`
  text-decoration: none;
`;

const ButtonStyled = styled(Button)`
  && {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
    padding: 16px 24px;

    &:hover {
      background: rgba(0, 0, 0, 0.2);
    }
  }
`;

const TextButton = styled(Typography)`
  && {
    color: #000;
    font-size: 20px;
    font-weight: 700;
    line-height: 24px;
    letter-spacing: 0.15px;
    text-transform: capitalize;
  }
`;

const ArrowStyled = styled(Arrow)`
  && {
    padding-left: 13px;
    box-sizing: content-box;
  }
`;

export {
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
};

export default {
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
};
