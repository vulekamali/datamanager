import React, { Component } from 'react';
import Markup from './Markup';



class Preview extends Component {
  constructor(props) {
    super(props);
    this.eventHandler = this.eventHandler.bind(this);

    this.state = {
      selected: this.props.department
    }

    this.events = {
      eventHandler: this.eventHandler.bind(this),
    }

    this.departmentNames = this.props.items.map(({ id, title }) => ({
      id,
      name: title
    }))
  }

  eventHandler(e) {
    if(e.target.value === this.state.selected) {
      return null;
    }

    const newUrl = `/${this.props.year}/previews/${this.props.sphere}/${this.props.government}/${e.target.value}`;
    window.history.pushState({}, window.document.title, newUrl );
    this.setState({ selected: e.target.value });
  }

  render() {
    const { state, events, props } = this;
    const selectedObject = props.items.find(({ id }) => id === state.selected);


    const passedProps = {
      ...props,
      ...selectedObject,
      eventHandler: events.eventHandler,
      selected: state.selected,
      government: props.government,
      departmentNames: this.departmentNames,
      year: props.year,
    };

    return <Markup {...passedProps } />
  }
}

export default Preview;

