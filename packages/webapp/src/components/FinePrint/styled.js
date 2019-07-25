import styled from 'styled-components';

import { Typography } from '@material-ui/core';


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
  margin-top: 16px;
  width: 100%;
  max-width: 1200px;

  @media screen and (min-width: 600px) {
    margin-top: 32px;
    margin-bottom: 32px;
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

export {
  FooterWrapper,
  FooterContainer,
  FooterDetails
}

export default {
  FooterWrapper,           
  FooterContainer,
  FooterDetails
}
