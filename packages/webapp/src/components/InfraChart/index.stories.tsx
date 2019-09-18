import React from 'react';
import { storiesOf } from '@storybook/react';
import InfraChart from './index';


const data = [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 0,
          "Connection": 0
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 15000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        }
      ]

const workingChart = () => <InfraChart {...{data}} />;


storiesOf('components.InfraChart', module)
  .add('workingChart', workingChart);
