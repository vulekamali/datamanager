/* eslint no-param-reassign: 0 */


import {zip} from 'lodash';
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
    const result = {labels: [], values: []};
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


const createModifyLabel = (target, fontString) => ({label, height, x, y, maxWidth}) => {
    const {textX, textY, align, color, space} = calcLabelPosition(height, x, y, maxWidth);
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


const dynamicLabelPlugin = ({chart}) => {
    const barInfo = chart.getDatasetMeta(0).data;
    const modifyLabel = createModifyLabel(chart.ctx, Chart.helpers.fontString);

    barInfo.forEach((bar) => {
        const {_xScale, _model} = bar;

        const {maxWidth} = _xScale;
        const {x, y, label, height} = _model;
        modifyLabel({label, height, x, y, maxWidth});
    });
};

const formatDataset = ({color, barTypes}) => (data, index) => {
    const [r, g, b] = colorString.get.rgb(color);
    const backgroundColor = `rgba(${r}, ${g}, ${b}, 0.${(index + 1) * 20})`;

    return {
        label: barTypes[index],
        data,
        'backgroundColor': barTypes[index] === 'Actual Expenditure' ? '#ee9f31' : backgroundColor,
        stack: barTypes[index],
        borderColor: '#fff',
        borderWidth: {
            top: barTypes[index] === 'Actual Expenditure' ? 1 : 0,
            left: 0,
            right: 0
        }
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
    const result = pivotedValues.map(formatDataset({color, barTypes}), []);
    return result;
};


const createChartJsConfig = ({items, rotated, color, viewportWidth, barTypes}) => {
    let {labels, values} = flattenNesting(items);
    const rotateLabels = viewportWidth && viewportWidth < 600 && rotated;
    let datasets = buildDatasets(barTypes, values, color);

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
                        const {index, datasetIndex} = item;
                        const {data, label} = dataObject.datasets[datasetIndex];
                        const prefix = barTypes ? `${label}: ` : '';

                        return `${prefix}R${trimValues(data[index])}`;
                    },
                    title: (data) => {
                        if (data.length <= 0) {
                            return;
                        }
                        return `${data[0].label} Q${data[0].datasetIndex - 3}`
                    }
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
                afterDatasetsDraw: rotated ? function (chart, options) {
                    let ctx = chart.chart.ctx;

                    ctx.textAlign = 'center';
                    ctx.fillStyle = '#fff';
                    ctx.font = "10px \"Helvetica Neue\", Helvetica, Arial, sans-serif";

                    datasets.forEach(function (dataset, i) {
                        if (dataset.stack !== 'Actual Expenditure') {
                            return
                        }
                        let meta = chart.controller.getDatasetMeta(i);
                        meta.data.forEach(function (bar, index) {
                            const y = bar._model.y + ((bar._model.base - bar._model.y) / 2) + 5;
                            ctx.fillText(`Q${i - 3}`, bar._model.x, y);
                        });
                    });
                } : dynamicLabelPlugin
            },
        ],
    };
};


export default createChartJsConfig;
