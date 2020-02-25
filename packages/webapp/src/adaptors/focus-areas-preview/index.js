import { createElement } from 'react';
import { render } from 'react-dom';

import Routing from './Routing';

const node = document.querySelector('[data-webapp="focus-areas-preview"]');
const financialYearSlug = node.getAttribute('data-year');
const component = createElement(Routing, {financialYearSlug});

const connection = () => {
  if (node) {
    render(component, node);
  }
};

export default connection();
