import normaliseExpenditure from './index.js';


const input = [
  { name: 'Administration', total_budget: 54671000 },
  { name: 'Intersectoral Coordination and Strategic Partnerships', total_budget: 24478000 },
  { name: 'Legislation and Policy Development', total_budget: 21392000 },
  { name: 'Civilian Oversight, Monitoring and Evaluations', total_budget: 30678000 },
];

const output = {
  Administration: 54671000,
  'Civilian Oversight, Monitoring and Evaluations': 30678000,
  'Intersectoral Coordination and Strategic Partnerships': 24478000,
  'Legislation and Policy Development': 21392000,
};


const basicCondition = () => expect(normaliseExpenditure(input)).toEqual(output);
test('basic', basicCondition);