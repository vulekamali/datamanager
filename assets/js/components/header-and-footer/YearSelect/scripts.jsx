import React from 'react';
import ReactDOM from 'react-dom';
import YearSelect from './index.jsx';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';
import DebounceFunction from './../../../utilities/js/helpers/DebounceFunction.js';


class YearSelectContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      open: false,
      tooltip: null,
      sticky: false,
    };

    this.node = null;
    this.updateNode = this.updateNode.bind(this);
    this.updateItem = this.updateItem.bind(this);
    this.data = this.normaliseData();

    this.updateSticky = () => {
      if (this.node) {
        const top = window.pageYOffset || document.documentElement.scrollTop;

        if (top < 200 && this.state.sticky) {
          return this.setState({ sticky: false });
        }

        if (top > 200 && !this.state.sticky) {
          this.setState({ sticky: true });
        }
      }

      return null;
    };

    const viewportDebounce = new DebounceFunction(50);
    const updateViewport = () => viewportDebounce.update(this.updateSticky);

    window.addEventListener(
      'resize',
      updateViewport,
    );

    window.addEventListener(
      'scroll',
      updateViewport,
    );
  }

  normaliseData() {
    return this.props.jsonData.reduce(
      (result, val) => {
        return [
          ...result,
          {
            direct: val.closest_match.is_exact_match,
            url: val.closest_match.url_path,
            name: val.id,
            active: val.is_selected,
          },
        ];
      },
      [],
    );
  }

  updateItem(key, value) {
    return this.setState({ [key]: value });
  }

  updateNode(node) {
    this.node = node;
  }

  render() {
    return (
      <YearSelect
        jsonData={this.data}
        search={this.props.search}
        loading={this.state.loading}
        open={this.state.open}
        updateItem={this.updateItem}
        tooltip={this.state.tooltip}
        updateNode={this.updateNode}
        sticky={this.state.sticky}
      />
    );
  }
}


function scripts() {
  const nodes = document.getElementsByClassName('js-initYearSelect');
  const nodesArray = [...nodes];
  const { no_js: noJs } = window.vulekamali.qs;

  if (nodesArray.length > 0 && !noJs) {
    nodesArray.forEach((node, i) => {
      const jsonData = JSON.parse(decodeHtmlEntities(nodes[i].getAttribute('data-json'))).data;

      ReactDOM.render(
        <YearSelectContainer {...{ jsonData }} />,
        nodes[i].parentNode,
        nodes[i],
      );
    });
  }
}


export default scripts();
