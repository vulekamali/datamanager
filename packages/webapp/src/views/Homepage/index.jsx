import React, { Component } from 'react';
import Markup from './Markup';



class Homepage extends Component {
  constructor(props) {
    super(props);
    this.eventHandler = this.eventHandler.bind(this);
    this.state = {
      modal: false,
      selected: null
    }

    this.events = {
      openModal: this.openModal.bind(this),
      closeModal: this.closeModal.bind(this),
      eventHandler: this.eventHandler.bind(this),
    }
  }

  openModal() {
    this.setState({ modal: true });
  }

  closeModal() {
    this.setState({ modal: false });
  }

  eventHandler(e) {
    this.setState({ selected: e });
  }

  render() {
    const { state, events, props } = this;

    const passedProps = {
      ...props,
      modal: state.modal,
      openModal: events.openModal,
      closeModal: events.closeModal,
      eventHandler: events.eventHandler,
      selected: state.selected
    };

    return <Markup {...passedProps } />
  }
}


export default Homepage;


// Homepage.propTypes = {
//   /** The heading text to use over the image */
//   heading: t.string.isRequired,
//   /** The smaller subheading text to user above the heading */
//   subheading: t.string.isRequired,
//   /** A single line of text to show as a notice just below image */
//   notice: t.string,
//   /** The Youtube video to use for the popup modal */
//   videoUrl: t.string,
//   /** The image to use as the background for the hero section */
//   image: t.string.isRequired,
//   /** A primary and secondary button to display over the image */
//   buttons: t.shape({
//     primary: t.shape({
//       text: t.string,
//       link: t.string,
//     }),
//     secondary: t.shape({
//       text: t.string,
//       link: t.string,
//     }),
//   }).isRequired,
//   /** A list of resources associated with this year's budget cycle */
//   resources: t.arrayOf(t.shape({
//     title: t.string,
//     size: t.string,
//     format: t.string,
//     link: t.string,
//   })),
//   /** A main call-to-action card that goes below the image and above the 'notice' line of text  */
//   callToAction: t.shape({
//     heading: t.string,
//     subheading: t.string,
//     button: t.shape({
//       text: t.string,
//       link: t.string,
//     }),
//   }),
// };


// Homepage.defaultProps = {
//   notice: null,
//   resources: null,
//   callToAction: null,
//   videoUrl: null,
// };
