import React, { Component } from 'react';

import Markup from './Markup';
import createColorGenerator from './generateColor';
import ResizeWindowListener from '../../helpers/ResizeWindowListener';
import modifyIfZoomed from './modifyIfZoomed';

const colorsList = createColorGenerator();

class Treemap extends Component {
  constructor(props) {
    super(props);

    const screenWidth = new ResizeWindowListener().stop();

    this.state = {
      selected: null,
      screenWidth,
      zoom: null,
    };

    this.events = {
      unsetZoomHandler: this.unsetZoomHandler.bind(this),
      changeSelectedHandler: this.changeSelectedHandler.bind(this),
    };

    const { items } = this.props;

    this.values = {
      items,
    };
  }

  componentDidMount() {
    this.values = {
      ...this.values,
      resizeListener: new ResizeWindowListener(this.changeWidthHandler.bind(this)),
    };
  }

  componentWillUnmount() {
    const { resizeListener } = this.values;

    if (resizeListener) {
      return resizeListener.stop();
    }

    return null;
  }

  unsetZoomHandler() {
    const { onSelectedChange } = this.props;

    if (onSelectedChange) {
      onSelectedChange(null);
    }

    return this.setState({
      selected: null,
      zoom: null,
    });
  }

  changeSelectedHandler(selected) {
    const { onSelectedChange } = this.props;

    if (onSelectedChange) {
      onSelectedChange(selected);
    }

    this.setState({
      selected: selected.id,
      zoom: selected.zoom || null,
    });
  }

  changeWidthHandler(screenWidth) {
    if (screenWidth >= 600) {
      this.setState({ screenWidth });
    }
  }

  render() {
    const { state, events, values } = this;
    const items = modifyIfZoomed(values.items, state.zoom);

    const passedProps = {
      ...state,
      ...events,
      items,
      fills: values.fills,
      hasChildren: values.hasChildren,
    };

    return <Markup {...passedProps} />;
  }
}

export default Treemap;
