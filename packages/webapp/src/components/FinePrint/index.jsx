import React from 'react';
import calcFineprint from './calcFineprint';

import {
  FooterWrapper,
  FooterContainer,
  FooterDetails
} from './styled';

const FinePrint = ({ year }) => (
  <FooterWrapper>
    <FooterContainer>
      <FooterDetails>{calcFineprint(year)}</FooterDetails>
    </FooterContainer>
  </FooterWrapper>
);

export default FinePrint;
