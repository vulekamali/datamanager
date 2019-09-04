import lunrSearchWrapper from './../lunrSearchWrapper.js';


const array1 = [
  {
    value: 'impsum',
    id: '1',
  },
  {
    value: 'lorem sum',
    id: '2',
  },
  {
    value: 'impsum lorem',
    id: '3',
  },
  {
    value: 'example',
    id: '4',
  },
];

const expected1 = [
  {
    value: 'lorem sum',
    id: '2',
  },
  {
    value: 'impsum lorem',
    id: '3',
  },
];

const ref1 = {
  2: [
    'lorem',
  ],
  3: [
    'lorem',
  ],
};

const result = lunrSearchWrapper(array1, 'id', 'value', 'lorem');

test('basic', () => {
  expect(result).toEqual([expected1, ref1]);
});

const array2 = [
  {
    value: 'impsum',
    other: 'impsum lorem',
    id: '1',
  },
  {
    value: 'lorem sum',
    other: 'impsum',
    id: '2',
  },
  {
    value: 'impsum lorem',
    other: 'example',
    id: '3',
  },
  {
    value: 'example',
    other: 'impsum lorem',
    id: '4',
  },
];

const ref2 = {
  1: [
    'lorem',
  ],
  2: [
    'sum',
  ],
  3: [
    'lorem',
  ],
  4: [
    'lorem',
  ],
};

const highlightResult2 = lunrSearchWrapper(array2, 'id', ['value', 'other'], 'sum lorem');
const result2 = [
  { id: '1', other: 'impsum lorem', value: 'impsum' },
  { id: '2', other: 'impsum', value: 'lorem sum' },
  { id: '3', other: 'example', value: 'impsum lorem' },
  { id: '4', other: 'impsum lorem', value: 'example' },
];

test('multiple-highlight', () => {
  expect(highlightResult2).toEqual([result2, ref2]);
});
