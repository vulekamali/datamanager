import React from 'react';

import { preactConnect as connect } from '../../utilities/js/helpers/connector.js';
import normaliseProgrammes from './services/normaliseProgrammes/index.js';
import normaliseSmallMultiples from './services/normaliseSmallMultiples/index.js';
import normaliseExpenditure from './services/normaliseExpenditure/index.js';
import normaliseExpenditurePhase from './services/normaliseExpenditurePhase/index.js';
import normaliseAdjusted from './services/normaliseAdjusted/index.js';
import normaliseExpenditureMultiples from './services/normaliseExpenditureMultiples/index.js';

import ChartSourceController from '../../components/ChartSourceController/index.jsx';



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
  const {
    scale, type, items: rawItems, title, subtitle, description, rotated, barTypes,
  } = props;
  const expenditure = type === 'expenditure'
    || type === 'expenditureMultiples'
    || type === 'expenditurePhase';

  const needToggle = type === 'expenditurePhase' || type === 'expenditure';
  const items = normaliseData({ type, rawItems, rotated });
  const color = expenditure ? '#ad3c64' : '#73b23e';

  let toggle;
  if (needToggle) {
    toggle = {
      "nominal": {
        "title": "Not adjusted for inflation"
      },
      "real": {
        "title": "Adjusted for inflation",
        "description": `The Rand values in this chart are adjusted for CPI inflation and are the effective \
      value in ${rawItems.base_financial_year.slice(0, 4)} Rands. CPI is used as the deflator, with the ${rawItems.base_financial_year} \
      financial year as the base.`
      }
    }
  } else {
    toggle = null;
  }

  const downloadText = {
    title,
    subtitle,
    description,
  };

  const styling = { scale, color, rotated };
  return React.createElement(ChartSourceController, {
    items, toggle, barTypes, styling, downloadText, type,
    inYearEnabled: rawItems.in_year_spending_enabled,
    departmentName: rawItems.department_name
  });
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
