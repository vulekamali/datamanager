/* eslint no-param-reassign: 0 */


import { zip } from 'lodash';
import colorString from 'color-string';

import Chart from 'chart.js';
import trimValues from '../../../../../../utilities/js/helpers/trimValues.js';
import isObjectLiteral from './services/isObjectLiteral/index.js';


const recursiveHeadingOverrides = (result, obj) => {
  Object.keys(obj).forEach((key) => {
    if (isObjectLiteral(obj[key])) {
      result.labels.push(`heading: ${key}`);
      result.values.push(0);

      return recursiveHeadingOverrides(result, obj[key]);
    }

    result.labels.push(key);
    result.values.push(obj[key]);
    return null;
  });
};

const flattenNesting = (obj) => {
  const result = { labels: [], values: [] };
  recursiveHeadingOverrides(result, obj);
  return result;
};

const calcLabelPosition = (height, x, y, maxWidth) => {
  if (x > maxWidth / 2) {
    return {
      textX: x - (height / 3),
      textY: y - 6,
      align: 'right',
      color: 'black',
      space: x - (((height / 3) * 2) + 20),
    };
  }

  return {
    textX: x + (height / 3),
    textY: y - 6,
    align: 'left',
    color: 'black',
    space: maxWidth - (x + (((height / 3) * 2) + 20)),
  };
};


const calcLabelTruncate = (target, space, label) => {
  let truncatedLabel = label;

  if (target.measureText(truncatedLabel).width < space) {
    return truncatedLabel;
  }

  for (let characters = label.length; characters >= 0; characters--) {
    truncatedLabel = truncatedLabel.substring(0, characters);
    if (target.measureText(truncatedLabel).width < space) {
      break;
    }
  }

  return `${truncatedLabel}...`;
};


const createModifyLabel = (target, fontString) => ({ label, height, x, y, maxWidth }) => {
  const { textX, textY, align, color, space } = calcLabelPosition(height, x, y, maxWidth);
  const fontFallbacks = '\'Source Sans\', sans-serif';

  const regexArray = label.match(/(^heading:\s)(.+)/im);
  const isHeading = /(^heading:\s)(.+)/im.test(label);
  const labelAfterHeadingCheck = isHeading ? regexArray[2] : label;
  const fontStyle = isHeading ? fontString(14, 'bold', fontFallbacks) : fontString(11, 'normal', fontFallbacks);

  const truncatedLabel = calcLabelTruncate(target, space, labelAfterHeadingCheck);

  target.font = fontStyle;
  target.textBaseline = 'top';
  target.fillStyle = isHeading ? 'grey' : color;
  target.textAlign = align;
  target.fillText(truncatedLabel, textX, isHeading ? textY + 3 : textY);
};


const dynamicLabelPlugin = ({ chart }) => {
  const barInfo = chart.getDatasetMeta(0).data;
  const modifyLabel = createModifyLabel(chart.ctx, Chart.helpers.fontString);

  barInfo.forEach((bar) => {
    const { _xScale, _model } = bar;

    const { maxWidth } = _xScale;
    const { x, y, label, height } = _model;
    modifyLabel({ label, height, x, y, maxWidth });
  });
};


const formatDataset = ({ color, barTypes }) => (data, index) => {
  const [r, g, b] = colorString.get.rgb(color);
  const backgroundColor = `rgba(${r}, ${g}, ${b}, 0.${(index + 1) * 20})`;

  return {
    label: barTypes[index],
    data,
    backgroundColor,
  };
};


const buildDatasets = (barTypes, values, color) => {
  if (!barTypes) {
    return [
      {
        data: values,
        backgroundColor: color
      },
    ];
  }

  const pivotedValues = zip(...values);
  const result = pivotedValues.map(formatDataset({ color, barTypes }), []);
  return result;
};


const createChartJsConfig = ({ items, rotated, color, viewportWidth, barTypes }) => {
  let { labels, values } = flattenNesting(items);
  const rotateLabels = viewportWidth && viewportWidth < 600 && rotated;
  console.log({labels, values, items})
  let datasets = buildDatasets(barTypes, values, color);
  if(barTypes.length === 11){
  	//todo: remove
  	labels =  ['2016-17', '2017-18', '2018-19', '2018-19', '2019-20']
  	values = [[10], [15], [20, 12], [12], [18]]
  	datasets = [{
  		data: [10, 12, 14, 16, 18],
  		backgroundColor: 'red',
  		stack: 'Stack 0'
  	},{
  		data: [20, 22, 24, 26, 28],
  		backgroundColor: 'blue',
  		stack: 'Stack 1'
  	},{
  		data: [null, 2, null, 6, null],
  		backgroundColor: 'black',
  		stack: 'Stack 1'
  	}]
  }
  if(barTypes.length === 5){
  	//todo: remove
  	console.log({datasets})
  }

  return {
    type: rotated ? 'bar' : 'horizontalBar',
    data: {
      labels,
      datasets,
    },
    options: {
      barThickness: 10,
      maintainAspectRatio: false,
      tooltips: {
        intersect: rotated,
        custom: (tooltip) => {
          if (!tooltip || /(^heading:\s)(.+)/im.test(tooltip.title)) {
            tooltip.opacity = 0;
            return;
          }
          tooltip.displayColors = false;
        },
        callbacks: {
          label: (item, dataObject) => {
            const { index, datasetIndex } = item;
            const { data, label } = dataObject.datasets[datasetIndex];
            const prefix = barTypes ? `${label}: ` : '';

            return `${prefix}R${trimValues(data[index])}`;
          },
        },
      },
      animation: {
        duration: 0,
      },
      layout: {
        padding: {
          top: 15,
          bottom: 15,
        },
      },
      legend: {
        display: false,
      },
      scales: {
        yAxes: [{
          barPercentage: 0.8,
          categoryPercentage: 1.0,
          display: true,
          gridLines: {
            color: 'transparent',
            display: true,
            drawBorder: false,
            zeroLineColor: '#ccc',
            zeroLineWidth: 1,
          },
          ticks: {
            display: rotated,
            beginAtZero: true,
            callback: value => (rotated ? `R${trimValues(value)}` : value),
          },
        }],
        xAxes: [{
          barPercentage: 1,
          stacked: true, 
          categoryPercentage: 0.6,
          ticks: {
            beginAtZero: true,
            maxRotation: rotateLabels ? 90 : 0,
            minRotation: rotateLabels ? 90 : 0,
            callback: value => (rotated ? value : `R${trimValues(value)}`),
          },
          gridLines: {
            color: 'transparent',
            display: true,
            drawBorder: false,
            zeroLineColor: '#ccc',
            zeroLineWidth: 1,
          },
        }],
      },
    },
    plugins: [
      {
        afterDatasetsDraw: rotated || dynamicLabelPlugin,
      },
    ],
  };
};


export default createChartJsConfig;
