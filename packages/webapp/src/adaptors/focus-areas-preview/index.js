import { createElement } from 'react';
import { render } from 'react-dom';

import DataLoader from './DataLoader';

const node = document.querySelector('[data-webapp="focus-areas-preview"]');

const initialise = () => {
  if (node) {
    const financialYearSlug = node.getAttribute('data-year');
    const focusAreaSlug = node.getAttribute('data-focus-area');
    const component = createElement(DataLoader, { financialYearSlug, focusAreaSlug });
    render(component, node);
  }
  return null;
};

export default initialise();
