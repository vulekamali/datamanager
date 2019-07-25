import React from 'react';
import Media from 'react-media';

import trimValues from '../../../helpers/trimValues';
import PieChart from '../../../components/PieChart';

import {
  Wrapper,
  Summary,
  Numbers,
  Budget,
  IntroMainHeading,
  IntroSubHeading,
  Percentages,
} from './styled';

const BudgetAmounts = (props) => {

  const {
    value,
    consolidated,
    sphere
  } = props;

  const newConsolidated = consolidated.toFixed(0);

  return (
    <Wrapper>
      <Summary>
        <Numbers>
          <Budget>
            <IntroMainHeading>
            <Media query="(max-width: 899px)">
              {matches =>
                matches ? (
                  `R${trimValues(value, true)}`
                ) : (
                  `R${trimValues(value)}`
                )
              }
            </Media>
            </IntroMainHeading>
            <IntroSubHeading>Original department budget</IntroSubHeading>
          </Budget>
          <Percentages>
            <div>
              <IntroMainHeading>
                <PieChart values={[newConsolidated]} /> {newConsolidated}%
              </IntroMainHeading>
              <IntroSubHeading>of {sphere} budget</IntroSubHeading>
            </div>
          </Percentages>
        </Numbers>
      </Summary>
    </Wrapper>
  );
};

export default BudgetAmounts;
