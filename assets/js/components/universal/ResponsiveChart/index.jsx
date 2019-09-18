import { h, Component } from 'preact';
import PropTypes from 'prop-types';
import Markup from './partials/Markup.jsx';
import DebounceFunction from './../../../utilities/js/helpers/DebounceFunction.js';


export default class ResponsiveChart extends Component {
  constructor(props) {
    super(props);
    const { minWidth } = this.props;

    this.state = {
      width: null,
      mobile: true,
    };

    this.static = {
      node: null,
      intervalRefresh: null,
    };

    this.events = {
      getNode: this.getNode.bind(this),
      viewportChange: this.viewportChange.bind(this),
    };

    const viewportDebounce = new DebounceFunction(300);
    const viewportChangeWrap = () => viewportDebounce.update(this.events.viewportChange);

    window.addEventListener(
      'resize',
      viewportChangeWrap,
    );
  }


  componentDidMount() {
    const delayedComponentMountedTasks = () => {
      const { viewportChange } = this.events;
      const { resizeAction } = this.props;

      if (viewportChange) {
        const width = viewportChange();
        return resizeAction ? resizeAction(width) : null;
      }

      return resizeAction;
    };

    return window.setTimeout(delayedComponentMountedTasks, 2000);
  }


  componentDidUpdate() {
    const { viewportChange } = this.events;
    const { resizeAction } = this.props;

    if (viewportChange) {
      const width = viewportChange();
      return resizeAction ? resizeAction(width) : null;
    }

    return null;
  }


  componentWillUnmount() {
    clearInterval(this.static.intervalRefresh);
  }


  getNode(node) {
    this.static.node = node;
    return null;
  }


  viewportChange() {
    const { node } = this.static || {};
    const { mobile, width: currentWidth } = this.state;
    const { minWidth, breakpoint } = this.props;
    const newWidth = node ? node.offsetWidth : null;

    if (mobile && window.innerWidth >= breakpoint) {
      this.setState({ mobile: false });
    } else if (!mobile && window.innerWidth < breakpoint) {
      this.setState({ mobile: true });
    }

    if (newWidth !== currentWidth) {
      if (newWidth <= minWidth && currentWidth !== minWidth) {
        return this.setState({ width: minWidth });
      }

      this.setState({ width: newWidth });
    }

    return newWidth || null;
  }


  render() {
    const { type, items, purple } = this.props;
    const { mobile, width } = this.state;
    const { getNode } = this.events;

    return (
      <Markup
        guides={!mobile}
        hover={!mobile}
        {...{ type, items, width, getNode, purple }}
      />
    );
  }
}


ResponsiveChart.propTypes = {
  type: PropTypes.oneOf(['bar', 'line']),
  minWidth: PropTypes.number,
  breakpoint: PropTypes.number,
  resizeAction: PropTypes.func,
  items: PropTypes.objectOf(PropTypes.arrayOf(PropTypes.number)).isRequired,
};


ResponsiveChart.defaultProps = {
  type: 'bar',
  resizeAction: null,
  minWidth: 250,
  breakpoint: 600,
};
