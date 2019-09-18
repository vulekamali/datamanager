import { h, render } from 'preact';
import ValueBlocks from './index.jsx';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';


function scripts() {
  const componentList = document.getElementsByClassName('js-initValueBlocks');

  for (let i = 0; i < componentList.length; i++) {
    const component = componentList[i];
    const items = JSON.parse(decodeHtmlEntities(component.getAttribute('data-values')));

    render(
      <ValueBlocks {...{ items }} />,
      component,
    );
  }
}


export default scripts();
