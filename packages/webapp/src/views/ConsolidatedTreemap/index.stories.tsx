import React, { Fragment } from 'react';
import { storiesOf } from '@storybook/react';
import faker from 'faker';
import { CssBaseline } from '@material-ui/core';

import { randomLengthBlankArray, randomNumber, randomBool } from '../../helpers/randomizer';
import ConsolidatedTreemap from './';

const iconsArray = [
  'social-development',
  'economic-affairs-and-agriculture',
  'defence',
  'debt-service-costs',
  'contingency-reserve',
  'general-admin',
  'economic-development',
  'health',
  'learning-and-culture',
  'local-development-and-infrastructure',
  'community-development',
  'peace-and-security',
  'general-public-services',
  'post-school-training',
];

const items = randomLengthBlankArray(35, 45).map((value, id) => ({
  id: faker.random.arrayElement(iconsArray),
  name: randomBool()
    ? faker.commerce.productName()
    : `${faker.commerce.productName()} ${faker.commerce.productName()}`,
  amount: randomNumber(5000, 5000000000),
  url: '#',
  percentage: randomNumber(1, 100),
}));

const initialSelected = {
  name: 'Consolidated Budget Summary',
  value: '92348259852',
  url: null,
  color: '#D8D8D8',
};

const basic = () => (
  <Fragment>
    <CssBaseline />
    <ConsolidatedTreemap {...{ items, initialSelected }} verb="Explore" subject="this department" />
  </Fragment>
);

storiesOf('views.ConsolidatedTreemap', module).add('Default', basic);
