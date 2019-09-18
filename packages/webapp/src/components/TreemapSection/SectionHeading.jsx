import React from 'react';
import SpeedDial from '../SpeedDial';

import {
  BudgetContainer,
  BudgetHeading,
  IconAndDates,
  DateButton,
 } from './styled';

const SectionHeading = () => (
  <BudgetContainer>
    <BudgetHeading>{isNationalBudget ? `National Budget Summary` : `Provincial Budget Summary`}</BudgetHeading>
    <IconAndDates>
      <SpeedDial />
      <div>
        <DateButton>2019-20</DateButton>
      </div>
    </IconAndDates>
  </BudgetContainer>
);

export default SectionHeading;
