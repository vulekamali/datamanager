import React from 'react';
import ResourceList from '../../components/ResourceList';
import Layout from '../../components/Layout';

import { Wrapper, Heading, ResourceWrapper } from './styled';

const Resources = ({ resources }) => (
  <Layout>
    <Wrapper>
      <Heading id="anchor">2019 budget resources</Heading>
      <ResourceWrapper>
        <ResourceList {...{ resources }} />
      </ResourceWrapper>
    </Wrapper>
  </Layout>
);

export default Resources;
