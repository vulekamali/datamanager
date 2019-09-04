import { h, Component } from 'preact';
import Chart from 'chart.js';
import PropTypes from 'prop-types';

import createChartJsConfig from './services/createChartJsConfig/index.js';
import downloadChart from './services/downloadChart/index.js';


const buildDownloadButton = downloadAction => (
  <div className="BarChart-button">
    <button
      className="Button is-small is-inline is-secondary"
      onClick={downloadAction}
    >
      Download chart
    </button>
  </div>
);


const Markup = ({ renderChart, height, downloadAction, rotated }) => {
  return (
    <div className="BarChart">
      <div className="BarChart-chart">
        <canvas ref={renderChart} style={{ width: '100%', height: `${rotated ? 350 : height}px` }} />
      </div>
      {/* {buildDownloadButton(downloadAction)} */}
    </div>
  );
};


Markup.propTypes = {
  renderChart: PropTypes.func.isRequired,
  height: PropTypes.number.isRequired,
  downloadAction: PropTypes.func.isRequired,
};


class BarChart extends Component {
  constructor(...props) {
    super(...props);
    const { items, color, rotated, viewportWidth, barTypes } = this.props;

    const calcHeight = (scale) => {
      const config = createChartJsConfig({ items, color, rotated, viewportWidth, barTypes });
      return (config.data.datasets[0].data.length * (25 * scale)) + 55;
    };


    this.values = {
      node: null,
      chartInstance: null,
    };

    this.events = {
      renderChart: this.renderChart.bind(this),
      downloadAction: this.downloadAction.bind(this),
      calcHeight,
    };
  }

  componentDidUpdate() {
    const { chartInstance } = this.values;
    const { items, color, rotated, barTypes } = this.props;

    const viewportWidth = window.innerWidth;
    const config = createChartJsConfig({ items, color, rotated, viewportWidth, barTypes });

    config.data.datasets.forEach(({ data }, index) => {
      chartInstance.data.datasets[index].data = data;
    });

    return chartInstance.update();
  }

  downloadAction(event) {
    event.preventDefault();
    const { items, color, rotated, downloadText, barTypes, source } = this.props;
    const config = createChartJsConfig({ items, color, rotated, barTypes });
    const { calcHeight } = this.events;
    const height = calcHeight(2);

    const canvas = document.createElement('canvas');
    const container = document.createElement('div');
    container.appendChild(canvas);
    document.body.appendChild(container);

    container.style.position = 'fixed';
    container.style.top = '200%';
    container.style.width = '800px';
    canvas.height = height;
    canvas.style.height = `${height}px`;

    new Chart(canvas, config);
    downloadChart({ canvas, height, downloadText, source });
  }

  renderChart(newNode) {
    const { items, color, rotated, barTypes } = this.props;
    const { node } = this.values;

    const viewportWidth = window.innerWidth;
    const config = createChartJsConfig({ items, color, rotated, viewportWidth, barTypes });
    this.values.chartInstance = new Chart(node || newNode, config);

    if (!node) {
      this.values.node = newNode;
    }

    return null;
  }


  render() {
    const { renderChart, downloadAction } = this.events;
    const { node } = this.state;
    const { scale, rotated } = this.props;
    const { calcHeight } = this.events;

    const height = calcHeight(scale);
    return <Markup button {...{ downloadAction, renderChart, height, node, rotated }} />;
  }
}


export default BarChart;

