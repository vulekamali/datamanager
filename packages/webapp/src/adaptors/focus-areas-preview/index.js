import { createElement } from 'react';
import { render } from 'react-dom';

import Routing from './Routing';

const node = document.querySelector('[data-webapp="focus-areas-preview"]')

const connection = () => {
  if (node) {
    render(createElement(Routing), node);
  }
};

export default connection();
