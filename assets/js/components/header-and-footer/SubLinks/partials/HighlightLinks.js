import buildLinksObject from './buildLinksObject.js';
import calcViewportPosition from './calcViewportPosition.js';


export default class HighlightLinks {
  // ...
  constructor(nodes) {
    // static values
    this.connectItemsObject = buildLinksObject(nodes);

    // stateful values
    this.selectedLink = {
      value: null,
      changed: false,
    };
    this.previousSelectedLink = {
      value: null,
      changed: false,
    };
    this.scrollTimeout = {
      value: null,
    };

    this.updateStateDebounce();
  }


  findCurrentViewedSection() {
    const pageMiddle = (window.innerHeight / 3);

    for (let i = this.connectItemsObject.length - 1; i >= 0; i--) {
      const link = this.connectItemsObject[i];
      const nodePositionFromTop = calcViewportPosition(link.target);
      const nodeFromMiddle = nodePositionFromTop + pageMiddle;

      if (nodeFromMiddle >= 0) {
        return i;
      }
    }

    return 0;
  }


  // ...
  updateState() {
    const currentScrolledSection = this.findCurrentViewedSection();

    if (currentScrolledSection !== this.selectedLink.value) {
      this.previousSelectedLink = {
        ...this.previousSelectedLink,
        value: this.selectedLink.value || 0,
        changed: true,
      };

      this.selectedLink = {
        ...this.selectedLink,
        value: currentScrolledSection,
        changed: true,
      };
    }

    this.updatePresentation();
  }


  updatePresentation() {
    if (this.selectedLink.changed) {
      this.connectItemsObject[this.selectedLink.value].link.classList.add('is-active');
      this.selectedLink.changed = false;
    }

    if (this.previousSelectedLink.changed) {
      if (this.selectedLink.value > 0) {
        this.connectItemsObject[0].link.classList.remove('is-active');
      }

      if (this.previousSelectedLink.value) {
        this.connectItemsObject[this.previousSelectedLink.value].link.classList.remove('is-active');
      }
      this.previousSelectedLink.changed = false;
    }
  }


  updateStateDebounce() {
    if (this.scrollTimeout.value) {
      clearTimeout(this.scrollTimeout.value);
    }

    const updateStateWrap = () => this.updateState();
    this.scrollTimeout.value = setTimeout(updateStateWrap, 5);
  }
}
