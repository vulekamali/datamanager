import React, { Component } from 'react';
import Markup from './Markup';



class TopBar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      sharingOpen: false,
      modalOpen: false,
    }

    this.events = {
      toggleModal: this.toggleModal.bind(this),
      toggleSharingOpen: this.toggleSharingOpen.bind(this),
    }
  }

  toggleModal(value = null) {
    return this.setState({ modal: value })
  }


  toggleSharingOpen() {
    const { sharingOpen: currentSharingOpen } = this.state;
    return this.setState({ sharingOpen: !currentSharingOpen })
  }

  render() {
    const { props, state, events } = this;

    const passedProps = {
      amount: props.amount,
      sharingOpen: state.sharingOpen,
      modal: state.modal,
      toggleSharingOpen: events.toggleSharingOpen,
      toggleModal: events.toggleModal,
      id: props.id,
      details: props.details,
      toggleDetails: props.toggleDetails,
      Link: props.Link,
      nextId: () => props.nextId(true),
      previousId: () => props.nextId(false),
    }

    return <Markup {...passedProps} />
  }
}


export default TopBar;


