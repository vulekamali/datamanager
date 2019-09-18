import React from 'react';
import { storiesOf } from '@storybook/react';

import ChartSection from './';

const data = [
  {
    name: "Police",
    value: "1234567",
    url: "#1",
    color: "#FFD54F"
  },
  {
    name: "Agriculture",
    value: "1463726",
    url: "#2",
    color: "#E57373"
  },
  {
    name: "Education",
    value: "6539209",
    url: "#3",
    color: "#4DD0E1"
  },
]

const initialSelected = {
  name: "National Budget Summary",
  value: "92348259852",
  url: null,
  color: "#D8D8D8"
}

const phases = {
  disabled: "Original budget",
}

const years = {
  disabled: "2018-19",
}

const Chart = ({ onSelectedChange }) => (
  <ul>
    {data.map(item => (
      <li
        key={item.name}
        onClick={() => onSelectedChange(item)}
      >
        <div>{item.name}</div>
        <div>{item.value}</div>
        <div>{item.url}</div>
      </li>
    ))}
  </ul>
);

const national = () => (
  <ChartSection
    {...{ data, initialSelected }}
    chart={(onSelectedChange) => <Chart {...{ onSelectedChange }} />}
    verb='Explore'
    subject='this department'
    footer='Budget data from 1 April 2018 - 31 March 2019'
    phases={phases}
    years={years}
    title='National Budget Summary'
  />
);

const provincial = () => (
  <ChartSection
    {...{ data, initialSelected }}
    chart={(onSelectedChange) => <Chart {...{ onSelectedChange }} />}
    verb='Explore'
    subject='this department'
    footer='Budget data from 1 April 2018 - 31 March 2019'
    phases={phases}
    years={years}
    title='Provincial Budget Summary'
  />
);



storiesOf('components.ChartSection', module)
  .add('National', national)
  .add('Provincial', provincial)
