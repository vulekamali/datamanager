import { createElement } from 'react';
import { render } from 'react-dom';
import Homepage from '../views/Homepage';

const node = document.querySelector('[data-webapp="homepage-hero"]');

const props = {
  image: 'https://via.placeholder.com/150',
  heading: node.dataset.mainHeading,
  subheading: node.dataset.subHeading,
  buttons: {
    primary: {
      text: node.dataset.primaryButtonLabel,
      link: node.dataset.primaryButtonUrl,
      target: node.dataset.primaryButtonTarget,
    },
    secondary: {
      text: node.dataset.secondaryButtonLabel,
      link: node.dataset.secondaryButtonUrl,
      target: node.dataset.secondaryButtonTarget,
    },
  },
  callToAction: {
    subheading: node.dataset.callToActionSubHeading,
    heading: node.dataset.callToActionHeading,
    link: {
      text: node.dataset.callToActionLinkLabel,
      link: node.dataset.callToActionLinkUrl,
      target: node.dataset.calToActionLinkTarget,
    },
  },
};

const connection = () => {
  if (node) {
    render(createElement(Homepage, props), node);
  }
};

export default connection();
