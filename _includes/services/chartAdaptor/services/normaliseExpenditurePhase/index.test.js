import normaliseExpenditurePhase from './index.js';


const input = {
  base_financial_year: '2017-18',
  nominal: [
    { amount: 82395000, financial_year: '2014-15', phase: 'Audited Outcome' },
    { amount: 117588000, financial_year: '2015-16', phase: 'Audited Outcome' },
    { amount: 99440000, financial_year: '2016-17', phase: 'Audited Outcome' },
    { amount: 124673000, financial_year: '2017-18', phase: 'Adjusted appropriation' },
    { amount: 131219000, financial_year: '2018-19', phase: 'Main appropriation' },
    { amount: 140469000, financial_year: '2019-20', phase: 'Medium Term Estimates' },
    { amount: 150292000, financial_year: '2020-21', phase: 'Medium Term Estimates' },
  ],
  real: [
    { amount: 96609177, financial_year: '2014-15', phase: 'Audited Outcome' },
    { amount: 131099606, financial_year: '2015-16', phase: 'Audited Outcome' },
    { amount: 104300427, financial_year: '2016-17', phase: 'Audited Outcome' },
    { amount: 124673000, financial_year: '2017-18', phase: 'Adjusted appropriation' },
    { amount: 124388085, financial_year: '2018-19', phase: 'Main appropriation' },
    { amount: 126465035, financial_year: '2019-20', phase: 'Medium Term Estimates' },
    { amount: 128205175, financial_year: '2020-21', phase: 'Medium Term Estimates' },
  ],
};

const output = {
  nominal: {
    '2014-15': 82395000,
    '2015-16': 117588000,
    '2016-17': 99440000,
    '2017-18': 124673000,
    '2018-19': 131219000,
    '2019-20': 140469000,
    '2020-21': 150292000,
  },
  real: {
    '2014-15': 96609177,
    '2015-16': 131099606,
    '2016-17': 104300427,
    '2017-18': 124673000,
    '2018-19': 124388085,
    '2019-20': 126465035,
    '2020-21': 128205175,
  },
};


const basicCondition = () => expect(normaliseExpenditurePhase(input)).toEqual(output);
test('basic', basicCondition);
