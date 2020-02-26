import React from 'react';
import ReactMarkdown from 'react-markdown';

import Heading from './Heading';
import ChartSection from '../../components/ChartSection';
import Treemap from '../../components/Treemap';
import Notices from './Notices';
import colorsList from '../../helpers/colorsList';
import polyfillObjectEntries from '../../helpers/polyfillObjectEntries.js';

import { Wrapper, FooterDetails } from './styled';

polyfillObjectEntries();

const addDynamicFootnotes = dynamicFootnotes =>
  dynamicFootnotes.map(footer => (
    <FooterDetails component="div">
      <ReactMarkdown source={footer} />
    </FooterDetails>
  ));

const callFootNote = dynamicFootnotes => (
  <div key={dynamicFootnotes}>
    {!!dynamicFootnotes && addDynamicFootnotes(dynamicFootnotes)}
    <FooterDetails>Flows between spheres have not been netted out.</FooterDetails>
  </div>
);

const callProvincialChart = (selected, initialSelected, items, footnotes, notices) => {
  if (Object.entries(items).length === 0) {
    return (
      <div key={`${selected}-provincial`}>
        <ChartSection
          {...{ initialSelected }}
          chart={() => <Notices {...{ notices }} />}
          title="Contributing provincial departments"
          footer={callFootNote(footnotes)}
        />
      </div>
    );
  }

  const addColors = (innerItems, overrideColor) =>
    innerItems.map((item, index) => ({
      ...item,
      color: overrideColor || colorsList[index],
      children: item.children ? addColors(item.children, overrideColor || colorsList[index]) : null,
    }));

  const transformData = item => ({
    ...item,
    id: item.id || item.name,
    children: !!item.children && item.children.map(transformData),
  });

  const itemKeys = Object.keys(items);
  const itemsAsArray = itemKeys.map(key => items[key]);
  const transformedItems = itemsAsArray.map(transformData);
  const itemsWithColor = addColors(transformedItems);

  return (
    <div key={`${selected}-provincial`}>
      <ChartSection
        {...{ initialSelected }}
        chart={onSelectedChange => <Treemap {...{ onSelectedChange }} items={itemsWithColor} />}
        verb="Explore"
        subject="this department"
        title="Contributing provincial departments"
        anchor="contributing-provincial-departments"
        footer={callFootNote(footnotes)}
      />
    </div>
  );
};

const Markup = props => {
  const {
    items,
    departmentNames,
    selected,
    eventHandler,
    initialSelectedNational,
    initialSelectedProvincial,
    financialYearSlug,
  } = props;

  const selectedInstance = items.find(({ id }) => id === selected);

  const itemsWithColor = selectedInstance.national.departments.map((item, index) => ({
    ...item,
    color: colorsList[index],
  }));

  return (
    <Wrapper>
      <Heading {...{ departmentNames, selected, eventHandler, financialYearSlug }} />
      <div key={`${selected}-national`}>
        <ChartSection
          initialSelected={initialSelectedNational}
          chart={onSelectedChange => <Treemap {...{ onSelectedChange }} items={itemsWithColor} />}
          verb="Explore"
          subject="this department"
          title="Contributing national departments"
          footer={callFootNote(selectedInstance.national.footnotes)}
        />
      </div>
      {callProvincialChart(
        selected,
        initialSelectedProvincial,
        selectedInstance.provincial.provinces,
        selectedInstance.provincial.footnotes,
        selectedInstance.provincial.notices,
      )}
    </Wrapper>
  );
};

export default Markup;
