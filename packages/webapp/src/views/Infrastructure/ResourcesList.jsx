import React from 'react';
import styled from 'styled-components';
import { Typography } from '@material-ui/core';
import ResourceList from '../../components/ResourceList';


const Wrapper = styled.div`
  background: #ededed;
  margin-top: 30px;
  padding-bottom: 100px;
`

const Content = styled.div`
  max-width: 1100px;
  margin: 0 auto;
`;

const Heading = styled(Typography)`
  && {
    font-size: 14px;
    font-weight: bold;
    font-family: Lato;
    padding: 40px 10px 15px;
    text-transform: uppercase;
    letter-spacing: 2px;
  }
`;


const ResourcesList = ({ resources }) => {
  return (
    <Wrapper>
      <Content>
        <Heading>Project Resources</Heading>
        <ResourceList {...{ resources }} />
      </Content>
    </Wrapper>
  );
}


export default ResourcesList;
