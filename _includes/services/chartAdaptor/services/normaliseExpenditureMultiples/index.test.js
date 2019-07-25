import normaliseExpenditureMultiples from './index.js';


const input = [
  {
    amount: 7125998600,
    financial_year: '2017-18',
    phase: 'Main Appropriation',
  },
  {
    amount: 7125998600,
    financial_year: '2017-18',
    phase: 'Adjusted Appropriation',
  },
  {
    amount: 6677034000,
    financial_year: '2017-18',
    phase: 'Final Appropriation',
  },
  {
    amount: 6422827800,
    financial_year: '2017-18',
    phase: 'Audited Appropriation',
  },
  {
    amount: 7855371000,
    financial_year: '2018-19',
    phase: 'Main Appropriation',
  },
  {
    amount: 717799810,
    financial_year: '2018-19',
    phase: 'Adjusted Appropriation',
  },
  {
    amount: null,
    financial_year: '2018-19',
    phase: 'Final Appropriation',
  },
  {
    amount: null,
    financial_year: '2018-19',
    phase: 'Audited Appropriation',
  },
  {
    amount: 7855371000,
    financial_year: '2019-20',
    phase: 'Main Appropriation',
  },
  {
    amount: null,
    financial_year: '2019-20',
    phase: 'Adjusted Appropriation',
  },
  {
    amount: null,
    financial_year: '2019-20',
    phase: 'Final Appropriation',
  },
  {
    amount: null,
    financial_year: '2019-20',
    phase: 'Audited Appropriation',
  },
];

const output = {
  '2017-18': [
    7125998600,
    7125998600,
    6677034000,
    6422827800,
  ],
  '2018-19': [
    7855371000,
    717799810,
    null,
    null,
  ],
  '2019-20': [
    7855371000,
    null,
    null,
    null,
  ],
};


const basicCondition = () => expect(normaliseExpenditureMultiples(input)).toEqual(output);
test('basic', basicCondition);

