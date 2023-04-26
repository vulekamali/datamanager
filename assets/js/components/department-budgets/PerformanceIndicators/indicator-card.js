import React, {Component} from "react";
import {Button, Card, Grid} from "@material-ui/core";
import * as d3 from "d3";

class IndicatorCard extends Component {
    constructor(props) {
        super(props);

        this.resizeObserver = null;

        this.state = {
            indicator: props.data,
            selectedQuarter: this.findLatestQuarter(props.data)
        }
    }

    componentDidMount() {
        this.handleObservers();
        this.handleAllCharts();
    }

    findLatestQuarter(data) {
        if (data['q4_actual_output'].trim() !== '') {
            return 4;
        } else if (data['q3_actual_output'].trim() !== '') {
            return 3;
        } else if (data['q2_actual_output'].trim() !== '') {
            return 2;
        } else {
            return 1;
        }
    }

    handleObservers() {
        const ps = document.querySelectorAll('.output-text-container .output-text');
        const padding = 24;
        if (this.resizeObserver === null) {
            this.resizeObserver = new ResizeObserver(entries => {
                for (let entry of entries) {
                    entry.target.parentElement.classList[entry.target.scrollHeight * 0.95 > entry.contentRect.height + padding ? 'add' : 'remove']('read-more-visible');
                }
            })
        }

        ps.forEach(p => {
            this.resizeObserver.observe(p);
        })
    }

    expandOutput(event) {
        const ele = event.target.parentElement.querySelectorAll('.output-text')[0]
        if (ele != null) {
            ele.style['-webkit-box-orient'] = 'unset';
        }
    }

    handleQuarterSelection(newVal) {
        this.setState({
            ...this.state,
            selectedQuarter: newVal
        });
    }

    renderQuarterSelection() {
        return (
            <Grid className={'quarter-selection-container'}>
                <Button
                    onClick={() => this.handleQuarterSelection(1)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.selectedQuarter === 1 ? 'selected' : ''}`}
                >Q1</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(2)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.selectedQuarter === 2 ? 'selected' : ''}`}
                >Q2</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(3)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.selectedQuarter === 3 ? 'selected' : ''}`}
                >Q3</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(4)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.selectedQuarter === 4 ? 'selected' : ''}`}
                >Q4</Button>
                <Button
                    onClick={() => this.handleQuarterSelection('Annual')}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.selectedQuarter === 'Annual' ? 'selected' : ''}`}
                >Full year</Button>
            </Grid>
        )
    }

    createChart(data, indicatorMax) {
        const width = 400;
        const height = 400;
        const margin = {top: 0, right: 0, bottom: 0, left: 0};

        const x = d3
            .scaleBand()
            .domain(data.map((d) => d.quarter))
            .rangeRound([margin.left, width - margin.right])
            .padding(0);

        const y = d3
            .scaleLinear()
            .domain([0, indicatorMax])  //max value
            .range([height - margin.bottom, margin.top]);

        const svg = d3.create("svg").attr("viewBox", [0, 0, width, height]);

        // bar
        svg
            .append("g")
            .attr("fill", "#f59e46")
            .selectAll("rect")
            .data(data)
            .join("rect")
            .attr("x", (d) => x(d.quarter))
            .attr("y", (d) => y(d.actual))
            .attr("height", (d) => y(0) - y(d.actual))
            .attr("width", x.bandwidth());

        // dashed line
        svg.append('line')
            .data(data)
            .attr('x1', margin.left)
            .attr('x2', width)
            .attr('y1', (d) => y(d.target))
            .attr('y2', (d) => y(d.target))
            .attr('stroke-width', 10)
            .style('stroke-dasharray', '8')
            .style('stroke', 'rgba(0, 0, 0, 0.7)')

        return svg.node();
    }

    isNumeric(str) {
        if (typeof str != 'string') {
            return false
        }

        return !isNaN(str) && !isNaN(parseFloat(str));
    }

    getIndicatorMax() {
        let valuesArr = [];
        for (let i = 1; i <= 4; i++) {
            const {target, actual} = this.getQuarterValues(i);
            valuesArr.push(this.isNumeric(target) ? parseFloat(target) : 0);
            valuesArr.push(this.isNumeric(actual) ? parseFloat(actual) : 0);
        }

        return Math.max(...valuesArr);
    }

    getQuarterValues(quarter) {
        const target = this.state.indicator[`q${quarter}_target`].replace('%', '').trim();
        const actual = this.state.indicator[`q${quarter}_actual_output`].replace('%', '').trim();

        return {target, actual};
    }

    handleChart(quarter) {
        const ctx = document.getElementById(`chart-${this.state.indicator.id}-${quarter}`);
        const {target, actual} = this.getQuarterValues(quarter);
        const bothNumeric = this.isNumeric(target) && this.isNumeric(actual);

        let values = bothNumeric ? [{
            quarter: `Q${quarter}`,
            actual: parseFloat(actual),
            target: parseFloat(target)
        }] : [{quarter: `Q${quarter}`, actual: 0, target: 0}]
        let indicatorMax = this.getIndicatorMax();

        const chart = this.createChart(values, indicatorMax);
        ctx.appendChild(chart)
    }

    handleAllCharts() {
        for (let i = 1; i <= 4; i++) {
            this.handleChart(i);
        }
    }

    renderChartContainers() {
        return (
            <Grid container spacing={2}>
                <Grid item xs={3}>
                    <div
                        style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                        id={`chart-${this.state.indicator.id}-1`}
                    />
                </Grid>
                <Grid item xs={3}>
                    <div
                        style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                        id={`chart-${this.state.indicator.id}-2`}
                    />
                </Grid>
                <Grid item xs={3}>
                    <div
                        style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                        id={`chart-${this.state.indicator.id}-3`}
                    />
                </Grid>
                <Grid item xs={3}>
                    <div
                        style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                        id={`chart-${this.state.indicator.id}-4`}
                    />
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    Q1
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    Q2
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    Q3
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    Q4
                </Grid>
            </Grid>
        )
    }

    renderCard() {
        return (
            <Grid item xs={4}>
                <Card
                    className={'programme-card'}
                >
                    <p className={'indicator-type'}>{this.state.indicator.type}</p>
                    <p className={'indicator-name'}>{this.state.indicator.indicator_name}</p>
                    {this.renderQuarterSelection()}
                    <Grid className={'indicator-section'}>
                        <p className={'section-head'}>QUARTER {this.state.selectedQuarter} TARGET:</p>
                        <div
                            className={'output-text-container'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                {this.state.indicator[`q${this.state.selectedQuarter}_target`]}
                            </div>
                            <div
                                className={'read-more-output'}
                            >
                                <svg width="9" height="7" viewBox="0 0 9 7" fill="none"
                                     xmlns="http://www.w3.org/2000/svg">
                                    <path d="M4.60604 6.07609L0.512102 0.711957L8.69998 0.711958L4.60604 6.07609Z"
                                          fill="#3F3F3F"/>
                                </svg>
                            </div>
                        </div>
                    </Grid>
                    <Grid className={'indicator-section'}>
                        <p className={'section-head'}>QUARTER {this.state.selectedQuarter} ACTUAL OUTPUT:</p>
                        <div
                            className={'output-text-container read-more-visible'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                {this.state.indicator[`q${this.state.selectedQuarter}_actual_output`]}
                            </div>
                            <button
                                className={'read-more-output'}
                                onClick={this.expandOutput}
                            >
                                <svg width="9" height="7" viewBox="0 0 9 7" fill="none"
                                     xmlns="http://www.w3.org/2000/svg">
                                    <path d="M4.60604 6.07609L0.512102 0.711957L8.69998 0.711958L4.60604 6.07609Z"
                                          fill="#3F3F3F"/>
                                </svg>
                            </button>
                        </div>
                    </Grid>
                    <Grid className={'indicator-section'}>
                        <p className={'section-head'}>QUARTER {this.state.selectedQuarter} PERFORMANCE:</p>
                        <div
                            className={'output-chart-container'}
                        >
                            {this.renderChartContainers()}
                        </div>
                    </Grid>
                </Card>
            </Grid>
        )
    }

    render() {
        return this.renderCard()
    }
}

export default IndicatorCard;