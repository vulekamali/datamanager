import React from 'react';
import styled from 'styled-components';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import { Typography } from '@material-ui/core';
import laptopImg from './laptop.jpg';
import arrowImg from './Shape.svg';

const Title = styled(Typography)`
  && {
    font-family: Roboto;
    font-size: 14px;
    letter-spacing: 0.01rem;
  }
`;

const CardWrapper = styled.div`
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  height: 100%;

  @media screen and (min-width: 600px) {
    max-width: 100%;
  }
`;

const StyledCard = styled(Card)`
  && {
    border-radius: 10px;
    width: 100%;
    box-shadow: 0px 13px 13px rgba(0, 0, 0, 0.12);
  }
`;

const CardContentWrapper = styled(CardContent)`
  &&&& {
    padding: 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    background: #F7F7F7;
    @media screen and (max-width: 375px) {
      width: auto;
      display: flex;
      flex-direction: column;
    }
  }
`;

const HeadingText = styled.div`
  &&&& {
    line-height: 23px;
    font-size: 16px;
    width: 60%;
    @media screen and (max-width: 675px){
      height: 100%;
      width: 100%;
    }
  }
`;

const TopImage = styled.div`
  height: 134px;
  background-image: url('${laptopImg}');
  background-position: 50% 50%;
  background-repeat: no-repeat;
  background-size: cover;
  @media screen and (min-width: 675px){
    display: none;
  }
`;


const ButtonBtn = styled(Button)`
  && {
    padding: 6px;
    min-width: 0;
    width: 40px;
    height: 57px;
    text-transform: none;
    box-shadow: none;
    
    @media screen and (max-width: 425px) {
      padding: 6px 16px;
      display: flex;
      justify-content: space-between;
      min-width: 193px;
      width: 100%;
      height: 32px;
    }
  }
`;

const TitleBlack = styled(Title)`
  && {
    color: #000;
    padding: 32px 96px 32px 32px;
    font-size: 24px;
    line-height: 150%;
    @media screen and (max-width: 425px){
      font-size: 18px;
      padding: 20px 25px 15px 25px;
      line-height: 173%;
    }
    @media screen and (max-width: 675px){
      padding-right: 32px;
    }
  }
`;

const ButtonExplore = styled(ButtonBtn)`
  &&{
    margin: 0 32px 32px 32px;
    background-color: #E5E5E5;
    color: white;
    width: auto;
    height: 64px;
    border-top-right-radius: 30px;
    border-bottom-right-radius: 30px;
    border-bottom-left-radius: 7px;
    border-top-left-radius: 7px;
    @media screen and (max-width: 425px){
      margin: 0 23px 22px 23px;
      height: 47px;
      width: 87%;
    }
    @media screen and (max-width: 340px){
      width: 86%
      line-height: 16px;
      padding-left: 7px;
    }
    &:hover {
      background-color: #D8D8D8;
    }
  }
`;


const SpanText = styled.span`
  font-size: 16px;
  font-weight: bold;
  color: #000000;
  position: relative;
  bottom: 5px;
  @media screen and (min-width: 425px){
    left: 20px;
  }
  @media screen and (max-width: 425px){
    font-size: 14px;
    padding-left: 0;
    bottom: 6px;
  }
  @media screen and (max-width: 335px){
    padding-left: 0;
    position: realative;
    left: 5px;
  }
`;

const StyledImage = styled.div`
  width: 40%;
  background-image: url('${laptopImg}');
  background-position: 50% 50%;
  background-repeat: no-repeat;
  background-size: cover;
  @media screen and (max-width: 674px) {
    display: none;
    width: 0;
  }
`;

const ArrowWrapper = styled.div`
  background: #ECA03E;
  padding: 15px;
  margin-left: 25px;
  width: 33px;
  height: 34px;
  border-radius: 35px;
  position: relative;
  left: 16px;
  bottom: 6px;
  @media screen and (max-width: 425px){
    width: 17px;
    height: 17px;
    margin-left: 0;
    border-radius: 25px;
  }
`;

const Arrow = styled.div`
  position: relative;
  top: 7px;
  left: 1px;
  @media screen and (max-width: 425px){
    top:0;
    left: 0;
  }
`;

const ArrowImage = styled.img`
  @media screen and (max-width: 425px){
    height: 15px;
  }
`;

const CallToAction = () => {

  return (
    <CardWrapper>
      <StyledCard>
        <CardContentWrapper>
          <HeadingText>
            <TopImage />
            <TitleBlack>
              We’ve added adjusted budget data to the 2017-18 National and Provincial budgets.
            </TitleBlack>
            <ButtonExplore variant="contained">
              <SpanText>Explore the adjusted budget</SpanText>
              <ArrowWrapper>
                <Arrow>
                  <ArrowImage src={arrowImg} alt="Arrow" />
                </Arrow>
              </ArrowWrapper>
            </ButtonExplore>
          </HeadingText>
            <StyledImage />
        </CardContentWrapper>
      </StyledCard>
    </CardWrapper>
  )
};


export default CallToAction;
