import React from 'react';
import styled from 'styled-components';
import { Typography } from '@material-ui/core';
import TopBar from './TopBar';
import Preview from './Preview';
import ProjectList from './ProjectList';
import Layout from '../../components/Layout';
import InfraChart from '../../components/InfraChart';
import ResourcesList from './ResourcesList';


const ChartWrap = styled.div`
  display: none;

  @media screen and (min-width: 500px) {
    display: block;
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px;
  }
`

const ChartHeading = styled(Typography)`
  && {
    font-size: 14px;
    font-weight: bold;
    font-family: Lato;
    padding: 40px 10px 15px;
    text-transform: uppercase;
    letter-spacing: 2px;
  }
`;

const HeadingAndKey = styled.div`
  display: flex;
  width: 100%;
  justify-content: space-between;
  max-width: 1000px;
`;

const BothKeysStyling = styled.div`
  display: flex;
  width: 400px;
  justify-content: space-between;
`;

const KeyStyling = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Line = styled.span`
  border-bottom: 3px solid #76B649;
  display: block;
  width: 20px;
  height: 3px;
  margin-right: 12px;
`;

const Text = styled(Typography)`
  && {
    font-family: Lato;
    margin: none;
    padding: none;
  }
`;

const DottedLine = styled.span`
  border-bottom: 3px dotted #76b649;
  height: 3px;
  width: 20px;
  margin-right: 12px;
`;

const Markup = (props) => {
  const {
    id,
    projects,
    nextId,
    details,
    toggleDetails,
    datasetUrl, 
    budgetReviewUrl,
    Link,
  } = props;

  const amount = projects.length;

  const topBarProps = {
    id,
    amount,
    details,
    toggleDetails,
    nextId,
    Link,
  }

  const buildChart = (details, data) => {
    if (!details || !data) {
      return null;
    }

    return (
      <ChartWrap>
        <HeadingAndKey>
          <ChartHeading>Expenditure Data</ChartHeading>
          <BothKeysStyling>
            <KeyStyling>
              <Line />
              <Text>Actual expenditure</Text>
            </KeyStyling>
            <KeyStyling>
              <DottedLine />
              <Text>Projected or adjusted budget</Text>
            </KeyStyling>
          </BothKeysStyling>
        </HeadingAndKey>
        <InfraChart {...{ data }} />
      </ChartWrap>
    )
  };
  
  return (
    <Layout>
      <TopBar {...topBarProps} />
      <Preview {...projects[id]} details={details} selected={id}  />
      {!details && <ProjectList {...{ projects, datasetUrl, budgetReviewUrl, Link }} />}
      {buildChart(details, projects[id].chartData)}
      {!!details && projects[id].resources.length > 0 && <ResourcesList resources={projects[id].resources || []} cite={projects[id].heading} />}
    </Layout>
  );
};


export default Markup;
