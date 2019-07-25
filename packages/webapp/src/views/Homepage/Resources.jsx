import React from 'react';
import styled from 'styled-components';
import { Typography } from '@material-ui/core';
import ResourceList from '../../components/ResourceList';


const Wrapper = styled.div`
  background: #f4f4f4;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px;
`;

const ResourceWrapper = styled.div`
  max-width: 1000px;
`;


const Heading = styled(Typography)`
&& {
  text-align: center;
  text-transform: uppercase;
  font-size: 14px;
  letter-spacing: 3px;
  font-family: Lato;
  padding: 10px;
}
`;

const Resources = ({ resources }) => (
  <Wrapper>
    <Heading id="anchor">2019 budget resources</Heading>
    <ResourceWrapper>
      <ResourceList {...{ resources }} />
    </ResourceWrapper>
  </Wrapper>
);


export default Resources;
