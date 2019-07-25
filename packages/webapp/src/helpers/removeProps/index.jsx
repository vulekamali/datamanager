
import { createElement } from 'react';


const forceToArray = value => (Array.isArray(value) ? value : [value]);
const notInsideArray = (array = []) => value => !array.find(arrayValue => arrayValue === value);


const createRemoveProps = initProps => outerProps => (props) => {
  const { createElement: scopedCreateElement } = initProps;

  const {
    component: Component,
    whitelist,
    blacklist = [],
  } = outerProps;

  const source = whitelist ? forceToArray(whitelist) : forceToArray(blacklist);
  const newPropsKeys = Object.keys(props).filter(notInsideArray(source));
  const newProps = newPropsKeys.reduce((result, key) => ({ ...result, [key]: props[key] }), {});
  return scopedCreateElement(Component, newProps, props.children);
};


export { createRemoveProps };
export default createRemoveProps({ createElement });
