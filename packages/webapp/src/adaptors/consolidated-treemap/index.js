import { createElement } from 'react';
import { render } from 'react-dom';

import DataLoader from './DataLoader';

const node = document.querySelector('[data-webapp="consolidated-treemap"]');

const initialise = () => {
  if (node) {
    const financialYearSlug = node.getAttribute('data-year');
    const component = createElement(DataLoader, {financialYearSlug});
    return render(component, node);
  }
  return null;
};

export default initialise();
