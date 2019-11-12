import React from 'react';
import ResourceList from '../../components/ResourceList';
import Layout from '../../components/Layout';

import { Wrapper, Heading, ResourceWrapper } from './styled';

const Resources = ({ resources, aeneResources }) => (
  <Layout>
    <Wrapper>
      <Heading id="adjustments-budget-resources">2019 adjustments budget resources</Heading>
      <ResourceWrapper>
        <ResourceList {...{ resources: aeneResources }} />
      </ResourceWrapper>
      <Heading id="budget-resources">2019 budget resources</Heading>
      <ResourceWrapper>
        <ResourceList {...{ resources }} />
      </ResourceWrapper>
    </Wrapper>
  </Layout>
);

export default Resources;
