import React, { Fragment } from 'react';
import { storiesOf } from '@storybook/react';
import faker from 'faker';
import { CssBaseline } from '@material-ui/core';

import { randomLengthBlankArray, randomNumber, randomBool } from '../../helpers/randomizer';
import NationalTreemap from './';

const items = randomLengthBlankArray(35, 45).map((value, id) => ({
  id,
  name: randomBool()
    ? faker.commerce.productName()
    : `${faker.commerce.productName()} ${faker.commerce.productName()}`,
  amount: randomNumber(5000, 5000000000),
  url: '#',
  percentage: randomNumber(1, 100),
}));

const initialSelected = {
  name: 'National Budget Summary',
  value: '92348259852',
  url: null,
  color: '#D8D8D8',
};

const basic = () => (
  <Fragment>
    <CssBaseline />
    <NationalTreemap {...{ items, initialSelected }} verb="Explore" subject="this department" />
  </Fragment>
);

storiesOf('views.NationalTreemap', module).add('Default', basic);
