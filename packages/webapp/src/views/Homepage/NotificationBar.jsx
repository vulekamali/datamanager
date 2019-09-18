import React from 'react';
import { darken } from 'polished';
import styled from 'styled-components';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import ForwardArrow from '@material-ui/icons/ArrowForward';
import constructionImg from './construction-workers.jpg';

const NoticeWrapper = styled.div`
  position: absolute;
  width: 100%;
  padding-bottom: 5px;
  font-family: Lato;
  font-size: 14px;
  line-height: 1.5;
  left: 0;
  top: ${({ hasCallToAction }) => (hasCallToAction ? 'calc(100% - 40px)' : 'auto')};
  bottom: ${({ hasCallToAction }) => (hasCallToAction ? 'auto' : 'calc(100% - 40px)')};

  @media (min-width: 650px) {
    padding-bottom: 15px;
    font-size: 16px;
  }
`;

const NoticeCard = styled(Card)`
  max-width: 280px;
  margin: 0 auto;

  && {
    box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.05), 0px 4px 4px rgba(0, 0, 0, 0.25);
  }

  @media (min-width: 450px) {
    max-width: 400px;
  }

  @media (min-width: 650px) {
    max-width: 550px;
  }
`;

const Text = styled(CardContent)`
  text-align: center;
  &&& {
    padding-top: 16px;
    padding-bottom: 16px;
    padding-right: 20px;
    padding-left: 20px;
  }
`;

const CallToActionPositionWrapper = styled.div`
  width: 100%;
  position: absolute;
  top: 210px;
  left: 0;

  @media (min-width: 650px) {
    top: 80px;
  }
`;

const CallToActionPosition = styled.div`
  position: relative;
  width: 100%;
  max-width: 280px;
  margin: 0 auto;

  @media (min-width: 450px) {
    max-width: 400px;
  }

  @media (min-width: 650px) {
    max-width: 550px;
  }
`;

const CallToAction = styled(Card)`
  position: absolute;
  width: 100%;
  bottom: 0;
  && {
    box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.05), 0px 4px 4px rgba(0, 0, 0, 0.25);
  }
`;

const Wrapper = styled.div`
  display: flex;
  background: #79B443;
  min-height: ${({ hasCallToAction }) => (hasCallToAction ? '265px' : '50px')};
  position: relative;
  justify-content: center;
  align-items: center;

  @media (min-width: 650px) {
    min-height: ${({ hasCallToAction }) => (hasCallToAction ? '135px' : '50px')};
  }
`;

const BuildPosition = styled(CardContent)`
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;

  &&& {
    padding: 0;
  }

  @media screen and (min-width: 650px) {
      flex-direction: row;
      height: 145px;
    }
`;

const ImgContainer = styled.div`
  height: 90px;
  background-image: url('${constructionImg}');
  background-size: cover;
  background-position: center;

  @media screen and (min-width: 650px) {
      flex-direction: row;
      width: 43%;
      height: 100%;
      order: 1;
    }
`;

const CallToActionDescription = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px;
  font-family: Lato;
  flex-grow: 1;

  @media screen and (min-width: 650px) {
    justify-content: space-around;
    width: 57%;
    flex-grow: 0;
    padding-left: 32px;
  }
`;

const CallToActionButton = styled(Button)`

  && {
    color: #fff;
    background-color: #79B443;
    font-size: 16px;
    font-weight: 700;
    font-family: Lato;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-transform: none;
    width: 100%
    padding-left: 24px;
    padding-right: 16px;

    &:hover {
      background: ${darken(0.1, '#79B443')};
    }

    @media screen and (min-width: 650px) {
      position: absolute;
      top: 50%;
      left: 290px;
      width: 200px;
    }
  }
`;

const CallToActionLink = styled.a`
  text-decoration: none;
`;

const BudgetTitle = styled.div`
  color: #79B443;
  font-weight: 700;
  font-size: 10px;
  text-transform: Uppercase;
  font-family: Lato;
  letter-spacing: 1px;
  padding-bottom: 12px;
`;

const BudgetHeading = styled.div`
  font-size: 16px;
  font-weight: 700;
  text-transform: Capitalize;
  padding-bottom: 16px;

  @media screen and (min-width: 650px) {
      font-size: 18px;
      max-width: 220px;
    }
`;

const buildNotice = (noticeText, hasCallToAction) => (
  <NoticeWrapper {...{ hasCallToAction }}>
    <NoticeCard>
      <Text>
        {noticeText}
      </Text>
    </NoticeCard>
  </NoticeWrapper>
);

const buildCallToAction = callToActionData => (
  <CallToActionPositionWrapper>
    <CallToActionPosition>
      <CallToAction>
        <BuildPosition>
          <ImgContainer />
          <CallToActionDescription>
            <BudgetTitle>{callToActionData.subheading}</BudgetTitle>
            <BudgetHeading>{callToActionData.heading}</BudgetHeading>
            <CallToActionLink href={callToActionData.link.link}>
              <CallToActionButton>
                <span>
                  {callToActionData.link.text}
                </span>
                <ForwardArrow />
              </CallToActionButton>
            </CallToActionLink>
          </CallToActionDescription>
        </BuildPosition>
      </CallToAction>
    </CallToActionPosition>
  </CallToActionPositionWrapper>
);

const NotificationBar = ({ notice: noticeText, callToAction: callToActionData }) => {
  return (
    <Wrapper hasCallToAction={!!callToActionData}>
      {noticeText && buildNotice(noticeText, !!callToActionData)}
      {callToActionData && buildCallToAction(callToActionData)}
    </Wrapper>
  );
};

// NotificationBar.propTypes = {
//   notice: t.string,
//   callToAction: t.shape({
//     subheading: t.string,
//     heading: t.string,
//     link: t.shape({
//       text: t.string,
//       link: t.string,
//     }),
//   }),
// };

// NotificationBar.defaultProps = {
//   notice: null,
//   callToAction: null,
// };

export default NotificationBar;
