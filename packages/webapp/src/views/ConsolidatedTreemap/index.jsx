import React, { Fragment } from 'react';
import MediaQuery from 'react-media';

import ChartSection from '../../components/ChartSection';
import Treemap from '../../components/Treemap';
import colorsList from '../../helpers/colorsList';
import mapFocusToIcon from './mapFocusToIcon';
import sortItems from './sortItems';

const footer = (financialYearInt) => (
  <Fragment>
    <div>
      Please note the above treemap is a representation of the allocation of the National Revenue
      Fund to functions of government.
    </div>
    <div>Budget data for the financial year 1 April {financialYearInt} - 31 March {financialYearInt+1}</div>
  </Fragment>
);

const Markup = ({ items, initialSelected, financialYearSlug, financialYearInt }) => {
  const sortedItems = sortItems(items);
  const itemsWithColor = sortedItems.map((item, index) => ({
    ...item,
    color: colorsList[index],
  }));

  const itemsWithIcons = itemsWithColor.map(item => ({
    ...item,
    icon: mapFocusToIcon(item.id),
  }));
  const footerMarkup = footer(financialYearInt);

  return (
    <ChartSection
      {...{ initialSelected, footerMarkup }}
      chart={onSelectedChange => <Treemap {...{ onSelectedChange }} items={itemsWithIcons} icons />}
      verb="Explore"
      subject="this focus area"
      title="Consolidated Budget Summary"
      phases={{
        disabled: 'Original budget',
      }}
      years={{
        disabled: financialYearSlug,
      }}
      anchor="consolidated-treemap"
    />
  );
};

const ConsolidatedTreemap = props => (
  <MediaQuery query="(min-width: 600px)">
    {matches => !!matches && <Markup {...props} />}
  </MediaQuery>
);

export default ConsolidatedTreemap;
