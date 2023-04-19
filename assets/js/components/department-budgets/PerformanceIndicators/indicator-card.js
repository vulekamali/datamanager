import React, {Component} from "react";
import {Button, Card, Grid} from "@material-ui/core";
import Chart from "chart.js";

class IndicatorCard extends Component {
    constructor(props) {
        super(props);

        this.resizeObserver = null;

        this.state = {
            indicator: props.data
        }
    }

    componentDidMount() {
        this.handleObservers();
        this.handleCharts();
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

    handleCharts() {
        const ctx = document.getElementById('chart-test');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Q3'],
                datasets: [{
                    label: '',
                    data: [15],
                    borderWidth: 0,
                    minBarLength: 100,
                    backgroundColor: ['#f59e46']
                }],
            },
            options: {
                legend: {
                    display: false,
                },
                scales: {
                    xAxes: [{
                        display: false
                    }],
                    yAxes: [{
                        beginAtZero: true,
                        display: false
                    }]
                }
            }
        });
    }

    renderCard() {
        return (
            <Grid item xs={4}>
                <Card
                    className={'programme-card'}
                >
                    <p className={'indicator-type'}>{this.state.indicator.type}</p>
                    <p className={'indicator-name'}>{this.state.indicator.name}</p>
                    <Grid className={'quarter-selection-container'}>
                        <Button variant={'contained'} className={'quarter-selection'}>Q1</Button>
                        <Button variant={'contained'} className={'quarter-selection'}>Q2</Button>
                        <Button variant={'contained'} className={'quarter-selection'}>Q3</Button>
                        <Button variant={'contained'} className={'quarter-selection'}>Q4</Button>
                    </Grid>
                    <Grid className={'indicator-section'}>
                        <p className={'section-head'}>QUARTER 3 TARGET:</p>
                        <div
                            className={'output-text-container'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                95
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
                        <p className={'section-head'}>QUARTER 3 ACTUAL OUTPUT:</p>
                        <div
                            className={'output-text-container read-more-visible'}
                        >
                            <div
                                className={'output-text'}
                                style={{
                                    WebkitBoxOrient: 'vertical'
                                }}
                            >
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                                Pellentesque non diam sit amet arcu malesuada rhoncus vel sit amet sem. Morbi quis
                                purus
                                vitae velit pulvinar imperdiet.
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
                        <p className={'section-head'}>QUARTER 3 PERFORMANCE:</p>
                        <div
                            className={'output-chart-container'}
                        >
                            <Grid container>
                                <Grid item xs={3}>
                                    <canvas
                                        id={'chart-test'}
                                    ></canvas>
                                </Grid>
                                <Grid item xs={3}>
                                    aa
                                </Grid>
                                <Grid item xs={3}>
                                    aa
                                </Grid>
                                <Grid item xs={3}>
                                    aa
                                </Grid>
                                <Grid item xs={3} className={'bar-text'}>
                                    Q1
                                </Grid>
                                <Grid item xs={3} className={'bar-text'}>
                                    Q2
                                </Grid>
                                <Grid item xs={3} className={'bar-text'}>
                                    Q3
                                </Grid>
                                <Grid item xs={3} className={'bar-text'}>
                                    Q4
                                </Grid>
                            </Grid>
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