import React from 'react';
import styled from 'styled-components';
import { Typography } from '@material-ui/core';
import Buttons from './Buttons';
import NotificationBar from './NotificationBar';
import parliamentImg from './parliament-building-budget-speech.jpg';
import Modal from './Modal';
import Layout from '../../components/Layout';



const Image = styled.div`
  background-image: url('${parliamentImg}');
  background-size: cover;
  background-position: center;
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
`;


const SubHeading = styled(Typography)`
  && {
    padding-top: 70px;
    font-size: 10px;
    color: #fff;
    text-transform: uppercase;
    padding-bottom: 5px;
    letter-spacing: 3px;
    font-family: Lato;
    text-align: center;

    @supports (display: flex) {
      padding-top: 0;
    }

    @media screen and (min-width: 650px) {
      font-size: 14px;
    }
  }
`;


const Heading = styled(Typography)`
  && {
    color: #fff;
    font-weight: 700;
    font-family: Lato;
    width: 90%;
    padding-bottom: 33px;
    line-height: 1;
    font-size: 28px;
    text-align: center;

    @media screen and (min-width: 650px) {
      font-size: 48px;
    }
  }
`;


const Markup = (props) => {
  const {
    buttons: buttonsRaw,
    heading,
    subheading,
    notice,
    resources,
    callToAction,
    modal,
    closeModal,
    openModal,
    videoUrl,
  } = props;

  const buttons = {
    ...buttonsRaw,
    primary: {
      ...buttonsRaw.primary,
      clickEvent: openModal,
    },
  }
  return (
    <Layout>
      <Modal {...{ closeModal, videoUrl }} open={!!modal} />
      <Image>
        <SubHeading>{subheading}</SubHeading>
        <Heading>{heading}</Heading>
        <Buttons primary={buttons.primary} secondary={buttons.secondary} />
      </Image>
      <NotificationBar {...{ notice, callToAction }} />
      <div data-webapp={'national-departments-treemap'}></div>
      <div data-webapp={'provincial-departments-treemap'}></div>
    </Layout>
  );
};


export default Markup;
