import React from 'react';
import ReactDOM from 'react-dom';
import Revenue from './index.jsx';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';


function scripts() {
  const componentList = document.getElementsByClassName('js-initRevenue');

  for (let i = 0; i < componentList.length; i++) {
    const component = componentList[i];

    const values = JSON.parse(decodeHtmlEntities(component.getAttribute('data-values')));
    const year = component.getAttribute('data-year');

    ReactDOM.render(
      <Revenue {...{ values, year }} />,
      component,
    );
  }
}


export default scripts();
