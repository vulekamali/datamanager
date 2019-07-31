import faker from 'faker';

// Type: Ttype
export type Ttype =
  | 'community'
  | 'dollar'
  | 'education'
  | 'family'
  | 'growth'
  | 'health'
  | 'money'
  | 'person'
  | 'plant'
  | 'police'
  | 'shield'
  | 'tap'
  | 'training';

export const iconTypes = [
  'community',
  'dollar',
  'education',
  'family',
  'growth',
  'health',
  'money',
  'person',
  'plant',
  'police',
  'shield',
  'tap',
  'training',
];

export const mockType = (): Ttype => faker.random.arrayElement(iconTypes);

// Type: Tprops
/**
 * All props accepted by the `<CustomIcon />` component.
 */
export type Tprops = {
  type: Ttype;
};

export const mockProps = (): Tprops => ({ type: mockType() });
