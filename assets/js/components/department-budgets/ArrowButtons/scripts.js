import DebounceFunction from '../../../utilities/js/helpers/DebounceFunction.js';


const calcAbsolutePositionFromTop = (node) => {
  const { top } = node.getBoundingClientRect();
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  return top + scrollTop;
};


function ArrowButtons() {
  const node = document.querySelector('[data-sticky-arrows]');
  const clickNodes = document.querySelectorAll('[data-scroll-smooth]');

  const clickOverride = (event, target) => {
    event.preventDefault();
    const targetNode = document.querySelector(target);
    const absoluteTop = calcAbsolutePositionFromTop(targetNode);
    const top = absoluteTop - 100;

    window.scrollTo({
      behavior: 'smooth',
      top,
    });
  };

  if (Array.from) {
    Array.from(clickNodes).forEach((innerNode) => {
      const target = innerNode.getAttribute('data-scroll-smooth');

      if (target) {
        innerNode.addEventListener(
          'click',
          event => clickOverride(event, target),
        );
      }
    });
  }

  const updateSticky = () => {
    if (node) {
      const active = node.classList.contains('is-active');
      const top = window.pageYOffset || document.documentElement.scrollTop;

      if (top < 700 && active) {
        return node.classList.remove('is-active');
      }

      if (top > 700 && !active) {
        return node.classList.add('is-active');
      }
    }

    return null;
  };

  const viewportDebounce = new DebounceFunction(50);
  const updateViewport = () => viewportDebounce.update(updateSticky);

  window.addEventListener(
    'resize',
    updateViewport,
  );

  window.addEventListener(
    'scroll',
    updateViewport,
  );
}


export default ArrowButtons();
