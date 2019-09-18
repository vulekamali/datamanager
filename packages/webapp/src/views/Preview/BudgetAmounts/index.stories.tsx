import React, { Fragment } from 'react';
import { CssBaseline } from '@material-ui/core';
import { storiesOf } from '@storybook/react';
import BudgetAmounts from './index';

const resources = {
  value: 372800000,
  consolidated: 37.344,
  sphere: 'national',
};

const basic = () => (
  <Fragment>
    <CssBaseline />
    <BudgetAmounts {...resources} />
  </Fragment>
);

storiesOf('components.BudgetAmounts', module).add('Default', basic);
