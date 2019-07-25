import React from 'react';

import SpeedDial from '../../../components/SpeedDial';
import { MenuItem } from '@material-ui/core';

import {
  Wrapper,
  BudgetContainer,
  BudgetHeadingAndShareIcon,
  BudgetHeading,
  FormContainer,
  BudgetPhase,
  SelectStyled,
  SelectStyledPhase,
  SpeedDialContainer,
 } from './styled';

 const callShareIcon = (share) => {
   if(!share) return null;

   if(typeof(share) === 'string') {
    return (
      <SpeedDialContainer>
        <SpeedDial {...{ share }} />
      </SpeedDialContainer>
     );
   }

   if(share) return (
    <SpeedDial />
   );
 }

 const callBudgetPhaseSelect = phases => (
    <BudgetPhase>
      <SelectStyledPhase disabled  displayEmpty classes={{ selectMenu: 'selectMenu', disabled: 'disabled', icon: 'icon' }}>
        <MenuItem>{phases.disabled}</MenuItem>
      </SelectStyledPhase>
    </BudgetPhase>
   );

 const callYearsSelect = years => (
  <SelectStyled disabled displayEmpty classes={{ selectMenu: 'selectMenu', disabled: 'disabled', icon: 'icon' }}>
    <MenuItem>{years.disabled}</MenuItem>
  </SelectStyled>
 );

 const callSelectDownOptions = (years, phases) => (
  <FormContainer>
    {phases && callBudgetPhaseSelect(phases)}
    {years && callYearsSelect(years)}
  </FormContainer>
 );

const SectionHeading = ({ title, share, years, phases }) => (
  <Wrapper>
    <BudgetContainer>
      <BudgetHeadingAndShareIcon>
        <BudgetHeading component='div'>{title}</BudgetHeading>
        {callShareIcon(share)}
      </BudgetHeadingAndShareIcon>
      {callSelectDownOptions(years, phases)}
    </BudgetContainer>
  </Wrapper>
);

export default SectionHeading;
