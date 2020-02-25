import { createElement } from 'react';
import { render } from 'react-dom';

import DataLoader from './DataLoader';

const node = document.querySelector('[data-webapp="provincial-treemap"]');
const financialYearSlug = node.getAttribute('data-year');
const component = createElement(DataLoader, {financialYearSlug});

const initialise = () => {
  if (node) {
    return render(component, node);
  }
  return null;
};

export default initialise();
