import { createElement } from 'react';
import { render } from 'react-dom';
import DataLoader from './DataLoader';

const node = document.querySelector('[data-webapp="preview-pages"]');

const connection = () => {
  if (node) {
    const financialYearSlug = node.getAttribute('data-year');
    const sphere = node.getAttribute('data-sphere');
    const government = node.getAttribute('data-government');
    const department = node.getAttribute('data-department');
    const props = { financialYearSlug, sphere, government, department };
    const component = createElement(DataLoader, props);
    render(component, node);
  }
};

export default connection();
