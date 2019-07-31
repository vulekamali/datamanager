import createTooltips from './index.js';


function scripts() {
  const parentNodes = document.getElementsByClassName('js-tooltips');
  createTooltips(parentNodes);
}


export default scripts();
