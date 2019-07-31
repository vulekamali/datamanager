import React from 'react';
import MediaQuery from 'react-media';

import ChartSection from '../../components/ChartSection';
import Treemap from '../../components/Treemap';

import colorsList from '../../helpers/colorsList';
import sortItems from './sortItems';

const addColors = (items, overrideColor) => {
  const sortedItems = sortItems(items);
  return sortedItems.map((item, index) => ({
    ...item,
    color: overrideColor || colorsList[index],
    children: item.children ? addColors(item.children, overrideColor || colorsList[index]) : null,
  }));
};

const transformData = item => ({
  ...item,
  id: item.id || item.name,
  children: !!item.children && item.children.map(transformData),
});

const Markup = ({ items, initialSelected }) => {
  const itemKeys = Object.keys(items);
  const itemsAsArray = itemKeys.map(key => items[key]);
  const transformedItems = itemsAsArray.map(transformData);
  const itemsWithColor = addColors(transformedItems);

  return (
    <ChartSection
      {...{ initialSelected }}
      footer="Budget data from 1 April 2018 - 31 March 2019"
      chart={onSelectedChange => <Treemap {...{ onSelectedChange }} items={itemsWithColor} />}
      verb="Explore"
      subject="this department"
      title="Provincial Budget Summary"
      phases={{
        disabled: 'Original budget',
      }}
      years={{
        disabled: '2018-19',
      }}
      anchor="provincial-treemap"
    />
  );
};

const ProvincialTreemap = props => (
  <MediaQuery query="(min-width: 600px)">
    {matches => !!matches && <Markup {...props} />}
  </MediaQuery>
);

export default ProvincialTreemap;
