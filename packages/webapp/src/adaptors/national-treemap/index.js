import { createElement } from 'react';
import { render } from 'react-dom';

import DataLoader from './DataLoader'

const node = document.querySelector('[data-webapp="national-treemap"]');
const component = createElement(DataLoader, {});

const initialise = () => {
  if (node) {
    return render(component, node);
  }
};

export default initialise();
