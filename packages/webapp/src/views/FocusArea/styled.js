import styled from 'styled-components';

import { Typography } from '@material-ui/core';

const Wrapper = styled.div`
  background: #fff;
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
  Wrapper,
  FooterDetails
}

export default {
  Wrapper,          
  FooterDetails
}
