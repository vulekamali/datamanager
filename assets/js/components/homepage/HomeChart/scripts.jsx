import { h, render, Component } from 'preact';
import DebounceFunction from './../../../utilities/js/helpers/DebounceFunction.js';
import getProp from './../../../utilities/js/helpers/getProp.js';
import HomeChart from './index.jsx';


class HomeChartContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      width: 200,
      mobile: true,
    };

    this.updateWidth = () => {
      if (this.state.mobile && window.innerWidth >= 600) {
        this.setState({ mobile: false });
      } else if (!this.state.mobile && window.innerWidth < 600) {
        this.setState({ mobile: true });
      }

      if (this.node && this.node.offsetWidth !== this.state.width) {
        if (this.node.offsetWidth <= 200 && this.state.width !== 200) {
          return this.setState({ width: 200 });
        }

        return this.setState({ width: parseInt(this.node.offsetWidth, 10) });
      }

      return null;
    };

    const viewportDebounce = new DebounceFunction(300);
    const updateViewport = () => viewportDebounce.update(this.updateWidth);

    window.addEventListener(
      'resize',
      updateViewport,
    );

    this.node = null;
    this.parentAction = this.parentAction.bind(this);
  }


  parentAction(node) {
    this.node = node;
    this.updateWidth();
  }


  render() {
    return (
      <HomeChart
        items={this.props.items}
        width={this.state.width}
        parentAction={this.parentAction}
        mobile={this.state.mobile}
        hasNull={this.props.hasNull}
      />
    );
  }
}


function scripts() {
  const nodes = document.getElementsByClassName('js-initHomeChart');

  const buildRevenueData = array => array.map((object) => {
    return {
      [object.category]: [object.amount],
    };
  });

  const buildExpenditureData = array => array.map((object) => {
    return {
      [object.name]: [parseInt(object.total_budget, 10)],
    };
  });

  const buildExpenditureDataWithNull = (array, yearString) => array.map((object) => {
    return {
      [object.name]: {
        link: `/${yearString}/search-result?search_type=full-search&search=${object.name}`,
      },
    };
  });

  const normaliseData = (array, hasNull, type, yearString) => {
    if (type === 'expenditure' && hasNull) {
      return buildExpenditureDataWithNull(array, yearString);
    } else if (type === 'expenditure') {
      return buildExpenditureData(array);
    } else if (type === 'revenue') {
      return buildRevenueData(array);
    }

    return {};
  };

  const calcIfHasNullTotalBudget = array => !array.every(object => object.total_budget !== null);


  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const rawValues = getProp('values', node, 'json');
    const type = getProp('type', node);
    const yearString = getProp('year', node);

    const hasNull = type === 'revenue' ? false : calcIfHasNullTotalBudget(rawValues.data);
    const items = Object.assign(...normaliseData(rawValues.data, hasNull, type, yearString));

    render(
      <HomeChartContainer {...{ hasNull, items }} />,
      node,
    );
  }
}


export default scripts();
