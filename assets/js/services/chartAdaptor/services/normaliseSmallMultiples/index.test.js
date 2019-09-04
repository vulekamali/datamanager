import normaliseSmallMultiples from './index.js';


const input = [
  {
    name: 'Current payments',
    type: 'economic_classification_1',
    items: [
      { name: 'Compensation of employees', total_budget: 22980000, type: 'economic_classification_2' },
      { name: 'Goods and services', total_budget: 7304000, type: 'economic_classification_2' },
    ],
  },
  {
    name: 'Payments for capital assets',
    type: 'economic_classification_1',
    items: [
      { name: 'Machinery and equipment', total_budget: 335000, type: 'economic_classification_2' },
      { name: 'Software and other intangible assets', total_budget: 59000, type: 'economic_classification_2' },
    ],
  },
];

const output = {
  data: {
    'Current payments': {
      'Compensation of employees': 22980000,
      'Goods and services': 7304000,
    },
    'Payments for capital assets': {
      'Machinery and equipment': 335000,
      'Software and other intangible assets': 59000,
    },
  },
};


const basicCondition = () => expect(normaliseSmallMultiples(input)).toEqual(output);
test('basic', basicCondition);
