import React, { Fragment } from 'react';
import MediaQuery from 'react-media';

import ChartSection from '../../components/ChartSection';
import Treemap from '../../components/Treemap';
import sortItems from './sortItems';

import colorsList from '../../helpers/colorsList.js';

const makeFooter = financialYearInt => (
  <Fragment>
    <div>
      Please note the above treemap is a representation of expenditure of national government
      departments.
    </div>
    <div>Budget data for the financial year 1 April { financialYearInt } - 31 March { financialYearInt +1 }</div>
    <div>Direct charges against the National Revenue Fund are excluded</div>
  </Fragment>
);

const Markup = ({ items, initialSelected, financialYearInt, financialYearSlug }) => {
  const sortedItems = sortItems(items);
  const itemsWithColor = sortedItems.map((item, index) => ({
    ...item,
    color: colorsList[index],
  }));

  const footer = makeFooter(financialYearInt);
  return (
    <ChartSection
      {...{ initialSelected, footer }}
      chart={onSelectedChange => <Treemap {...{ onSelectedChange }} items={itemsWithColor} />}
      verb="Explore"
      subject="this department"
      title="National Budget Summary"
      phases={{
        disabled: 'Original budget',
      }}
      years={{
        disabled: '2019-20',
      }}
      anchor="national-treemap"
    />
  );
};

const NationalTreemap = props => (
  <MediaQuery query="(min-width: 600px)">
    {matches => !!matches && <Markup {...props} />}
  </MediaQuery>
);

export default NationalTreemap;
