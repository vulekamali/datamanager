import faker from 'faker';
import { mockType, Ttype } from '../CustomIcon/schema';

//Type: Tcolor
/**
 * TODO: Zeeshaan add description
 */
export type Tcolor = string;
export const mockColor = (): Tcolor => faker.internet.color();

//Type: Turl
/**
 * TODO: Zeeshaan add description
 */
export type Turl = string;
export const mockUrl = (): Turl => faker.internet.url();

//Type: Tname
/**
 * TODO: Zeeshaan add description
 */
export type Tname = string;
export const mockName = (): Tname => faker.commerce.productName();

//Type: Tid
/**
 * TODO: Zeeshaan add description
 */
export type Tid = string;
export const mockId = (): Tid => faker.random.uuid();

//Type: Tamount
/**
 * TODO: Zeeshaan add description
 */
export type Tamount = number;
export const mockAmount = (): Tamount => parseInt(faker.finance.amount(100000000, 980000000));

//Type: Ticon
export type Ticon = Ttype;
export const mockIcon = (): Ttype => mockType();

//Type: TbaseItem
/**
 * TODO: Zeeshaan add description
 */
export type TbaseItem = {
  amount: Tamount;
  id: Tid;
  name: Tname;
  url: Turl | null;
  color: Tcolor;
  icon: Ticon | null;
};

export const mockBaseItem = (color): TbaseItem => ({
  amount: mockAmount(),
  id: mockId(),
  name: mockName(),
  url: faker.random.boolean() ? mockUrl() : null,
  color: color || mockColor(),
  icon: faker.random.boolean() ? mockIcon() : null,
});

// Type: Tchildren
export type Tchildren = TbaseItem[];
export const mockChildren = (color: Tcolor) =>
  new Array(faker.random.number({ min: 1, max: 12 })).fill(true).map(() => mockBaseItem(color));

// Type: TparentItem
export type TparentItem = TbaseItem & { children?: Tchildren };
export const mockParentItem = () => {
  const item = mockBaseItem();

  return {
    ...item,
    children: faker.random.boolean() ? mockChildren(item.color) : null,
  };
};

//Type: TonSelectedChange
export type TonSelectedChange = (TbaseItem) => void | null;
export const mockOnSelectedChange = (): TonSelectedChange => console.log;

// Type: Tprops
/**
 * All the props accepted accepted by the `<Treemap />` component.
 */
export type Tprops = {
  items: TparentItem[];
  onSelectedChange?: TonSelectedChange;
};

export const mockProps = (): Tprops => ({
  items: new Array(faker.random.number({ min: 2, max: 35 })).fill(true).map(mockParentItem),
  onSelectedChange: faker.random.boolean ? mockOnSelectedChange : null,
});

// Type: TscreenWidth
export type TscreenWidth = number;
export const mockScreenWidth = (): TscreenWidth => faker.random.number({ min: 0, max: 1920 });

// Type: Tstate
/**
 * TODO: Zeeshaan add description
 */
export type Tstate = {
  selected: Tid | null;
  zoom: Tid | null;
  screenWidth: TscreenWidth;
};

export const getIdAndZoom = ({ id, children }: { id: Tid; children?: Tchildren }) => {
  if (!children) {
    return { selected: id, zoom: null };
  }
  return { selected: faker.random.arrayElement(children).id, zoom: id };
};

export const mockState = (items: TparentItem[]): Tstate => {
  const listOfIdsAndZoomCombinations = items.map(getIdAndZoom);
  const idAndZoomCombinations = faker.random.arrayElement(listOfIdsAndZoomCombinations);
  return {
    ...idAndZoomCombinations,
    screenWidth: mockScreenWidth(),
  };
};
