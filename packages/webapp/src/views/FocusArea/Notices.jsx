import React from 'react';
import styled from 'styled-components';

import { Typography } from '@material-ui/core';

const Wrapper = styled.div`
  background-color: rgba(0, 0, 0, 0.04);
  ${'' /* background-color: red; */}
  padding-top: 16px;
  padding-bottom: 16px;
`;

const Text = styled(Typography)`
  && {
    font-weight: 700;
    font-size: 18px;
    line-height: 25px;
    text-align: center;
    color: #000;
  }
`;

const callText = notices => notices.map(notice => (
  <Text key={notice}>{notice}</Text>
));

const Notices = ({ notices }) => (
  <Wrapper>
    {callText(notices)}
  </Wrapper>
);

export default Notices;
