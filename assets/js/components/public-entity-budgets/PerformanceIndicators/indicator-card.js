import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Button, Card, Grid, Tooltip} from "@material-ui/core";
import {scaleLinear, scaleBand} from "d3-scale";
import {create} from "d3-selection";

class IndicatorCard extends Component {
    constructor(props) {
        super(props);

        this.resizeObserver = null;

        this.state = {
            indicator: props.data,
            selectedQuarter: this.findLatestQuarter(props.data),
            selectedPeriodType: props.data.frequency === 'annually' ? 'annual' : 'quarter',
            selectedYear: props.financialYear,   // current year in default
            previousYearsIndicators: props.previousYearsIndicators,
            financialYear: props.financialYear
        }
    }

    componentDidMount() {
        this.handleObservers();

        if (this.state.indicator == null) {
            return;
        }

        if (this.state.indicator.frequency === 'annually') {
            this.handleAnnualCharts();
        } else {
            this.handleQuarterlyCharts();
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevState.selectedPeriodType !== this.state.selectedPeriodType && this.state.selectedPeriodType === 'annual') {
            this.handleAnnualCharts();
        }

        if (this.props.previousYearsIndicators !== this.state.previousYearsIndicators) {
            this.setState({
                ...this.state,
                previousYearsIndicators: this.props.previousYearsIndicators
            });

            if (this.state.indicator.frequency === 'annually') {
                this.handleAnnualCharts();
            }
        }
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
            selectedQuarter: newVal,
            selectedPeriodType: 'quarter'
        });
    }

    handlePeriodTypeSelection(newVal) {
        this.setState({
            ...this.state,
            selectedPeriodType: newVal
        });
    }

    renderQuarterSelection() {
        return (
            <Grid className={'quarter-selection-container'}>
                <Button
                    onClick={() => this.handleQuarterSelection(1)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.indicator != null && this.state.indicator.frequency === 'annually' ? 'hidden-quarter' : ''} ${this.state.selectedQuarter === 1 && this.state.selectedPeriodType === 'quarter' ? 'selected' : ''}`}
                >Q1</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(2)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.indicator != null && this.state.indicator.frequency === 'annually' ? 'hidden-quarter' : ''} ${this.state.selectedQuarter === 2 && this.state.selectedPeriodType === 'quarter' ? 'selected' : ''}`}
                >Q2</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(3)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.indicator != null && this.state.indicator.frequency === 'annually' ? 'hidden-quarter' : ''} ${this.state.selectedQuarter === 3 && this.state.selectedPeriodType === 'quarter' ? 'selected' : ''}`}
                >Q3</Button>
                <Button
                    onClick={() => this.handleQuarterSelection(4)}
                    variant={'contained'}
                    className={`quarter-selection ${this.state.indicator != null && this.state.indicator.frequency === 'annually' ? 'hidden-quarter' : ''} ${this.state.selectedQuarter === 4 && this.state.selectedPeriodType === 'quarter' ? 'selected' : ''}`}
                >Q4</Button>
                <Button
                    onClick={() => this.handlePeriodTypeSelection('annual')}
                    variant={'contained'}
                    className={`quarter-selection float-right ${this.state.selectedPeriodType === 'annual' ? 'selected' : ''}`}
                >Full year</Button>
            </Grid>
        )
    }

    isNumeric(str) {
        if (typeof str != 'string') {
            return false
        }

        return !isNaN(str) && !isNaN(parseFloat(str));
    }

    getIndicatorQuarterMax() {
        let valuesArr = [];
        for (let i = 1; i <= 4; i++) {
            const {target, actual} = this.getQuarterTargetAndActual(i);
            valuesArr.push(this.isNumeric(target) ? parseFloat(target) : 0);
            valuesArr.push(this.isNumeric(actual) ? parseFloat(actual) : 0);
        }

        return Math.max(...valuesArr);
    }

    getIndicatorAnnualMax(financialYear) {
        let valuesArr = [];
        for (let i = 3; i >= 0; i--) {
            const {target, actual} = this.getAnnualTargetAndActual(financialYear);
            valuesArr.push(this.isNumeric(target) ? parseFloat(target) : 0);
            valuesArr.push(this.isNumeric(actual) ? parseFloat(actual) : 0);
        }

        return Math.max(...valuesArr);
    }

    getQuarterKeyValue(appix, annualAppix, quarter) {
        const prefix = this.state.selectedPeriodType === 'annual' ? '' : 'q';
        const finalAppix = this.state.selectedPeriodType === 'annual' ? annualAppix : appix;
        const key = `${prefix}${quarter}_${finalAppix}`;
        if (this.state.selectedPeriodType === 'annual' && this.state.selectedYear !== this.state.financialYear) {
            const indicator = this.state.previousYearsIndicators.filter(x => x.financialYear === this.state.selectedYear)[0].indicator;
            return indicator == null ? null : indicator[key];
        } else {
            return this.state.indicator[key];
        }
    }

    renderQuarterKeyValue(appix, annualAppix, quarter = this.state.selectedQuarter) {
        const val = this.getQuarterKeyValue(appix, annualAppix, quarter);
        const elem = (val == null || val.trim() === '') ?
            <span className={'data-not-available'}>Data not yet available</span> : <span>{val}</span>

        return elem;
    }

    getQuarterKeyText(appix, annualAppix) {
        const prefix = this.state.selectedPeriodType === 'annual' ? `${this.state.selectedYear} ANNUAL` : 'QUARTER';
        const finalAppix = this.state.selectedPeriodType === 'annual' ? annualAppix : appix;
        const quarter = this.state.selectedPeriodType === 'annual' ? '' : this.state.selectedQuarter;
        return `${prefix} ${quarter} ${finalAppix}`;
    }

    createChart(data, indicatorMax) {
        const width = 400;
        const height = 400;
        const margin = {top: 0, right: 0, bottom: 0, left: 0};

        const x = scaleBand()
            .domain(data.map((d) => d.quarter))
            .rangeRound([margin.left, width - margin.right])
            .padding(0);

        const y = scaleLinear()
            .domain([0, indicatorMax])  //max value
            .range([height - margin.bottom, margin.top]);

        const svg = create("svg").attr("viewBox", [0, 0, width, height]);

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

    createUnavailableChartIndicator(quarter, nonNumeric) {
        const svgElement = <svg width="36" height="35" viewBox="0 0 36 35" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
            <circle cx="17.7084" cy="17.5" r="17.5" fill="#B9B9B9"/>
            <path d="M16.6527 12.2227V9.68359H19.3969V12.2227H16.6527ZM16.6527 24V13.6289H19.3969V24H16.6527Z"
                  fill="#3F3F3F"/>
        </svg>
        return (
            <div
                className={'unavailable-chart-indicator'}
            >
                <Tooltip
                    title={`${quarter} ${nonNumeric} is qualitative. See value above by selecting appropriate period.`}
                    placement={'top'}
                >
                    {svgElement}
                </Tooltip>
            </div>
        )
    }

    getQuarterTargetAndActual(quarter) {
        const target_init = this.getQuarterKeyValue('target', 'target', quarter);
        const actual_init = this.getQuarterKeyValue('actual_output', 'audited_output', quarter);
        const target = target_init == null ? 0 : target_init.replace('%', '').trim();
        const actual = actual_init == null ? 0 : actual_init.replace('%', '').trim();

        return {target, actual};
    }

    handleQuarterChart(quarter) {
        const ctx = document.getElementById(`chart-quarter-${this.state.indicator.id}-${quarter}`);
        const {target, actual} = this.getQuarterTargetAndActual(quarter);
        const bothNumeric = this.isNumeric(target) && this.isNumeric(actual);

        if (bothNumeric) {
            // show chart
            let values = [{
                quarter: `Q${quarter}`,
                actual: parseFloat(actual),
                target: parseFloat(target)
            }];
            let indicatorMax = this.getIndicatorQuarterMax();

            const chart = this.createChart(values, indicatorMax);
            ctx.appendChild(chart)
        } else {
            // chart is not available
            const nonNumeric = !this.isNumeric(actual) ? 'actual output' : 'target';
            const parentDiv = this.createUnavailableChartIndicator(`Q${quarter}`, nonNumeric);

            ReactDOM.render(parentDiv, ctx);
        }
    }

    getAnnualTargetAndActual(financialYear) {
        const indicator = this.state.previousYearsIndicators.filter(x => x.financialYear === financialYear)[0].indicator;
        const target = indicator == null ? 0 : indicator['annual_target'].replace('%', '').trim();
        const actual = indicator == null ? 0 : indicator['annual_audited_output'].replace('%', '').trim();

        return {target, actual};
    }

    handleAnnualCharts() {
        for (let i = 1; i <= 4; i++) {
            if (this.state.previousYearsIndicators[i - 1] != null) {
                const financialYear = this.state.previousYearsIndicators[i - 1].financialYear;
                const ctx = document.getElementById(`chart-annual-${this.state.indicator.id}-${i}`);
                if (!ctx.hasChildNodes()) {
                    const {target, actual} = this.getAnnualTargetAndActual(financialYear);
                    const bothNumeric = this.isNumeric(target) && this.isNumeric(actual);

                    if (bothNumeric) {
                        // show chart
                        let values = [{
                            quarter: financialYear,
                            actual: parseFloat(actual),
                            target: parseFloat(target)
                        }]

                        let indicatorMax = this.getIndicatorAnnualMax(financialYear);

                        const chart = this.createChart(values, indicatorMax);
                        ctx.appendChild(chart)
                    } else {
                        // chart is not available
                        const nonNumeric = !this.isNumeric(actual) ? 'actual output' : 'target';
                        const parentDiv = this.createUnavailableChartIndicator(financialYear, nonNumeric);

                        ReactDOM.render(parentDiv, ctx);
                    }
                }
            }
        }
    }

    handleQuarterlyCharts() {
        for (let i = 1; i <= 4; i++) {
            this.handleQuarterChart(i);
        }
    }

    getQuarterChartContainer(q) {
        return (
            <Grid
                key={`chart-quarter-container-${this.state.indicator.id}-${q}`}
                item
                xs={3}
                style={{
                    cursor: 'pointer',
                    display: this.state.selectedPeriodType === 'annual' ? 'none' : 'block'
                }}
                className={this.state.selectedQuarter === q ? 'active-chart' : ''}
                onClick={() => {
                    this.setState({
                        ...this.state,
                        selectedQuarter: q
                    })
                }}
            >
                <div
                    style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                    id={`chart-quarter-${this.state.indicator.id}-${q}`}
                />
            </Grid>
        )
    }

    getAnnualChartContainer(q) {
        if (this.state.previousYearsIndicators.length <= q - 1 || this.state.previousYearsIndicators[q - 1] == null) {
            return;
        }

        const selectedYear = this.state.previousYearsIndicators[q - 1].financialYear;
        return (
            <Grid
                key={`chart-annual-container-${this.state.indicator.id}-${q}`}
                item
                xs={3}
                style={{
                    cursor: 'pointer',
                    display: this.state.selectedPeriodType === 'annual' ? 'block' : 'none'
                }}
                className={this.state.selectedYear === selectedYear ? 'active-chart' : ''}
                onClick={() => {
                    this.setState({
                        ...this.state,
                        selectedYear: selectedYear
                    })
                }}
            >
                <div
                    style={{backgroundColor: 'rgba(63, 63, 63, 0.08)', borderRadius: '2px'}}
                    id={`chart-annual-${this.state.indicator.id}-${q}`}
                />
            </Grid>
        )
    }

    renderChartContainerColumns() {
        return (
            [1, 2, 3, 4].map(q => {
                return ([
                    this.getQuarterChartContainer(q),
                    this.getAnnualChartContainer(q)
                ])
            })
        )
    }

    renderChartContainers() {
        return (
            <Grid container spacing={2}>
                {this.renderChartContainerColumns()}
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    {this.state.selectedPeriodType === 'annual' && this.state.previousYearsIndicators[0] !== undefined ? this.state.previousYearsIndicators[0].financialYear : 'Q1'}
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    {this.state.selectedPeriodType === 'annual' && this.state.previousYearsIndicators[1] !== undefined ? this.state.previousYearsIndicators[1].financialYear : 'Q2'}
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    {this.state.selectedPeriodType === 'annual' && this.state.previousYearsIndicators[2] !== undefined ? this.state.previousYearsIndicators[2].financialYear : 'Q3'}
                </Grid>
                <Grid item xs={3} className={'bar-text'} style={{paddingTop: '0px'}}>
                    {this.state.selectedPeriodType === 'annual' && this.state.previousYearsIndicators[3] !== undefined ? this.state.previousYearsIndicators[3].financialYear : 'Q4'}
                </Grid>
            </Grid>
        )
    }

    renderCard() {
        return (
            <Grid item sm={4} xs={12}>
                <Card
                    className={'programme-card'}
                >
                    <p className={'indicator-type'}>TYPE: {this.state.indicator.type}</p>
                    <p className={'indicator-name'}>{this.state.indicator.indicator_name}</p>
                    {this.renderQuarterSelection()}
                    <Grid className={'indicator-section'}>
                        <p className={'section-head'}>{this.getQuarterKeyText('TARGET', 'TARGET')}:</p>
                        <div
                            className={'output-text-container'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                {this.renderQuarterKeyValue('target', 'target', this.state.selectedPeriodType === 'annual' ? 'annual' : this.state.selectedQuarter)}
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
                        <p className={'section-head'}>{this.getQuarterKeyText('ACTUAL OUTPUT', 'AUDITED PERFORMANCE')}:</p>
                        <div
                            className={'output-text-container read-more-visible'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                {this.renderQuarterKeyValue('actual_output', 'audited_output', this.state.selectedPeriodType === 'annual' ? 'annual' : this.state.selectedQuarter)}
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
                        <p className={'section-head'}>
                            <span>{this.getQuarterKeyText('PERFORMANCE', 'PERFORMANCE')}:</span>
                            <span className={'chart-legend'}>
                                <span>
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                                         xmlns="http://www.w3.org/2000/svg">
<rect x="0.666718" y="0.5" width="15" height="15" rx="2" fill="#F59E46
"/>
</svg>
                                </span>
                                <span style={{marginRight: '10px', marginLeft: '5px'}}>Actual</span>
                                <span>
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
                                         xmlns="http://www.w3.org/2000/svg">
<rect x="0.666718" y="0.5" width="15" height="15" rx="2" fill="black" fillOpacity="0.06"/>
<line x1="1.66672" y1="7.5" x2="14.6667" y2="7.5" stroke="black" strokeOpacity="0.7" strokeDasharray="2 2"/>
</svg>
                                </span>
                                <span style={{marginLeft: '5px'}}>Target</span>
                            </span>
                        </p>
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