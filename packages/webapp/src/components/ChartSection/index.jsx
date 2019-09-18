import React, { Component } from 'react';
import Markup from './Markup';

class ChartSection extends Component {
  constructor(props) {
    super(props);
    const { initialSelected } = this.props;

    this.state = {
      selected: initialSelected || null,
    };

    this.events = {
      onSelectedChange: this.onSelectedChange.bind(this),
    };
  }

  onSelectedChange(event) {
    const { initialSelected } = this.props;

    if (event === null) {
      return this.setState({ selected: initialSelected });
    }

    this.setState({ selected: event });
  }

  render() {
    const { state, events, props } = this;

    const passedProps = {
      ...props,
      selected: state.selected,
      onSelectedChange: events.onSelectedChange,
    };

    return <Markup {...passedProps} />;
  }
}

export default ChartSection;
