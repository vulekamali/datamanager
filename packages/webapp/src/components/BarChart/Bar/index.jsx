import React, { Component } from 'react';

import Markup from './Markup';
import ResizeWindowListener from '../../../helpers/ResizeWindowListener';
import { colors } from './data';


class Bar extends Component {
  constructor(props) {
    super(props);
    this.state = {
      labelOutside: null,
    }

    this.values = {
      fills: colors,
      componentNode: React.createRef(),
      textNode: React.createRef(),
    };
  }

  componentDidMount () {
    this.values = {
      ...this.values,
      resizeListener: new ResizeWindowListener(this.labelOutsideHandler.bind(this)),
    }
    this.labelOutsideHandler();
  }

  labelOutsideHandler() {
    const { componentNode, textNode } = this.values;
    const { clientWidth: ColorBarWidth} = componentNode.current;
    const { clientWidth: TextWidth } = textNode.current;

    if (TextWidth >= ColorBarWidth) {
      return this.setState({ labelOutside: true });
    }

    return this.setState({ labelOutside: false });
  }

  componentWillUnmount() {
    const { resizeListener } = this.values;

    if (resizeListener) {
      return resizeListener.stop();
    }

    return null;
  }

  render() {
    const { state, props, values } = this;

    const passedProps = {
      ...props,
      ...state,
      labelOutside: state.labelOutside,
      textNode: values.textNode,
      componentNode: values.componentNode,
      fills: values.fills,
    };

    return <Markup {...passedProps } />
  }
}

export default Bar;
