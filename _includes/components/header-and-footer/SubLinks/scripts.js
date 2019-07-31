import FixedNodeBox from './partials/FixedNodeBox.js';
import HighlightLinks from './partials/HighlightLinks.js';
import forceClose from './partials/forceClose.js';


function scripts() {
  const nodes = document.getElementsByClassName('SubLinks is-currentPage');

  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];

    if (node) {
      const fixedListener = new FixedNodeBox(node);
      const fixedWrapper = () => fixedListener.updateStateDebounce();
      window.addEventListener('scroll', fixedWrapper);

      const linksList = node.getElementsByClassName('js-link');

      if (linksList.length > 0) {
        const highlightListener = new HighlightLinks(linksList);
        const highlightWrapper = () => highlightListener.updateStateDebounce();
        window.addEventListener('scroll', highlightWrapper); //
      }

      forceClose(linksList);
    }
  }
}


export default scripts();
