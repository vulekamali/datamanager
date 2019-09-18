import React from 'react';

import trimValues from '../../helpers/trimValues';
import { TooltipText, StyledTooltip } from './styled';

const TooltipContent = ({ name, amount }) => {
  return (
    <StyledTooltip>
      <TooltipText bold>{name}</TooltipText>
      <TooltipText>R{trimValues(amount, true)}</TooltipText>
    </StyledTooltip>
  );
};

export default TooltipContent;
