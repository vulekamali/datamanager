import React from 'react';

import { preactConnect as connect } from '../../utilities/js/helpers/connector.js';
import normaliseProgrammes from './services/normaliseProgrammes/index.js';
import normaliseSmallMultiples from './services/normaliseSmallMultiples/index.js';
import normaliseExpenditure from './services/normaliseExpenditure/index.js';
import normaliseExpenditurePhase from './services/normaliseExpenditurePhase/index.js';
import normaliseAdjusted from './services/normaliseAdjusted/index.js';
import normaliseExpenditureMultiples from './services/normaliseExpenditureMultiples/index.js';

import ChartSourceController from '../../components/ChartSourceController/index.jsx';
import { toggleValues } from './data.json';


const normaliseData = ({ type, rawItems }) => {
  switch (type) {
    case 'multiple': return normaliseSmallMultiples(rawItems);
    case 'programmes': return normaliseProgrammes(rawItems);
    case 'expenditure': return normaliseExpenditure(rawItems);
    case 'adjusted': return normaliseAdjusted(rawItems);
    case 'expenditureMultiples': return normaliseExpenditureMultiples(rawItems);
    case 'expenditurePhase': return normaliseExpenditurePhase(rawItems);
    default: return null;
  }
};


const ChartAdaptor = (props) => {
  const { scale, type, items: rawItems, title, subtitle, description, rotated, barTypes } = props;
  const expenditure = type === 'expenditure'
  || type === 'expenditureMultiples'
  || type === 'expenditurePhase';

  const needToggle = type === 'expenditurePhase' || type === 'expenditure';
  const items = normaliseData({ type, rawItems, rotated });
  const color = expenditure ? '#ad3c64' : '#73b23e';
  const toggle = needToggle ? toggleValues : null;

  const downloadText = {
    title,
    subtitle,
    description,
  };

  const styling = { scale, color, rotated };
  return React.createElement(ChartSourceController, { items, toggle, barTypes, styling, downloadText });
};


const query = {
  type: 'string',
  items: 'json',
  scale: 'number',
  color: 'string',
  title: 'string',
  subtitle: 'string',
  description: 'string',
  rotated: 'boolean',
  barTypes: 'json',
};


export default connect(ChartAdaptor, 'ChartAdaptor', query);
