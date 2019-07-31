import React from 'react';
import styled from 'styled-components';
import CircularProgress from '@material-ui/core/CircularProgress';
import Layout from '../../components/Layout';


const Wrapper = styled.div`
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  & .color {
    color: rgb(121, 180, 67);
  }
`;


export default () => (
  <Layout>
    <Wrapper>
      <CircularProgress size={65} classes={{ colorPrimary: 'color' }} />
    </Wrapper>
  </Layout>
);
 