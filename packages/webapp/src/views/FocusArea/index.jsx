import React, { Component } from 'react';
import Markup from './Markup';

class Preview extends Component {
  constructor(props) {
    super(props);
    this.eventHandler = this.eventHandler.bind(this);

    this.state = {
      selected: this.props.focusAreaSlug,
    };

    this.events = {
      eventHandler: this.eventHandler.bind(this),
    };

    this.departmentNames = this.props.items.map(({ id, name }) => ({
      id,
      name,
    }));
  }

  eventHandler(e) {
    const { updateUrl } = this.props;
    if (e.target.value === this.state.selected) {
      return null;
    }
    if (updateUrl) {
      const newUrl = `/${this.props.financialYearSlug}/focus/${e.target.value}`;
      window.history.pushState({}, window.document.title, newUrl);
    }
    this.setState({ selected: e.target.value });
  }

  render() {
    const { state, events, props } = this;

    const selectedkey = props.items.findIndex(({ id }) => id === state.selected);
    const selectedObject = props.items[selectedkey];

    const initialSelectedNational = {
      name: 'National Department Contributions',
      value: selectedObject.national.total,
      url: null,
      color: '#D8D8D8',
    };

    const initialSelectedProvincial = {
      name: 'Provincial Department Contributions',
      value: selectedObject.provincial.total,
      url: null,
      color: 'rgba(0, 0, 0, 0.1)',
    };

    const passedProps = {
      ...props,
      eventHandler: events.eventHandler,
      selected: state.selected,
      government: props.government,
      departmentNames: this.departmentNames,
      initialSelectedNational,
      initialSelectedProvincial,
    };

    return <Markup {...passedProps} />;
  }
}

export default Preview;
