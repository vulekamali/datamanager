import React from 'react';
import { storiesOf } from '@storybook/react';
import BarChart from './index';

const items = [
  {
    title: 'Administration',
    amount: 695320000000
  },
  {
    title: 'Economic Statistics',
    amount: 493210000000
  },
  {
    title: 'Population & Social Statistics',
    amount: 202300000000
  },
  {
    title: 'Methodology, Standards & Reasearch',
    amount: 67400000000
  },
  {
    title: 'Statistical Support & Informatics',
    amount: 267100000000
  },
  {
    title: 'Statistical Collection & Outreach',
    amount: 608000000000
  },
  {
    title: 'Survey Operations',
    amount: 194740000000
  }
]

const basic = () => <BarChart {...{ items }} />;


storiesOf('components.BarChart', module)
  .add('Default', basic)
