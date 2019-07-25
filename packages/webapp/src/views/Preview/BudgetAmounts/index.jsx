import React from 'react';
import Media from 'react-media';

import { Tooltip } from '@material-ui/core';
import trimValues from '../../../helpers/trimValues';
import PieChart from '../../../components/PieChart';
import calcTotal from './calcTotal';

import {
  Wrapper,
  Summary,
  Numbers,
  Budget,
  IntroMainHeading,
  IntroSubHeading,
  Percentages,
  TooltipStyled,
} from './styled';

const BudgetAmounts = props => {
  const { value, consolidated, sphere } = props;
  return (
    <Wrapper>
      <Summary>
        <Numbers>
          <Budget>
            <IntroMainHeading>
              <Media query="(max-width: 899px)">
                {matches => (matches ? `R${trimValues(value, true)}` : `R${trimValues(value)}`)}
              </Media>
            </IntroMainHeading>
            <IntroSubHeading>Original department budget</IntroSubHeading>
          </Budget>
          <Percentages>
            <TooltipStyled />
            <Tooltip
              title={`${consolidated.toPrecision(3)}%`}
              placement="top-start"
              classes={{ tooltip: 'previewPercentageTooltip' }}
            >
              <div>
                <IntroMainHeading>
                  <PieChart values={[consolidated < 1 ? 1 : consolidated]} />{' '}
                  {calcTotal(consolidated)}%
                </IntroMainHeading>
                <IntroSubHeading>of {sphere} budget</IntroSubHeading>
              </div>
            </Tooltip>
          </Percentages>
        </Numbers>
      </Summary>
    </Wrapper>
  );
};

export default BudgetAmounts;
