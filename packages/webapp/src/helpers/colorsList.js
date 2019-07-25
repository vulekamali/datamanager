import { flatten } from 'lodash';
import polyfillArrayFill from './polyfillArrayFill';

const colors = [
  '#FFD54F',
  '#E57373',
  '#4DD0E1',
  '#7986CB',
  '#BA68C8',
  '#4DB6AC',
  '#A1887F',
  '#64B5F6',
  '#FF8A65',
];

polyfillArrayFill();

const colorsList = flatten(new Array(50).fill(true).map(() => colors));

export default colorsList;
