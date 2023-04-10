import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Button, Card, Grid, Paper} from "@material-ui/core";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            open: false, triggered: false, programmes: [{
                name: 'Programme 2: Social Assistance',
                indicators: [{
                    name: 'Number of SSPs capacitated on psycho-social support guidelines',
                    type: 'STANDARDISED INDICATOR'
                }, {
                    name: 'Monthly payment of social grant beneficiaries as administered and paid by SASSA on behalf of DSD',
                    type: 'STANDARDISED INDICATOR'
                }, {
                    name: 'Number of SSPs capacitated on Social and Behaviour Change (SBC) programmes',
                    type: 'STANDARDISED INDICATOR'
                }]
            }]
        };
    }

    setOpen() {
        console.log({'open': this})
        this.setState({
            ...this.state, open: !this.state.open
        });
    }

    renderReadMoreButton() {
        if (this.state.open) {
            return;
        }

        return (<div>
            <div className="IntroSection-fade"/>
            <div className="IntroSection-button">
                <button className="Button is-secondary is-inline" onClick={() => this.setOpen()}>Read
                    More
                </button>
            </div>
        </div>)
    }

    renderIndicatorCards(programme) {
        return programme.indicators.map((indicator) => {
            return (
                <Grid item xs={4}>
                    <Card
                        className={'programme-card'}
                    >
                        <p className={'indicator-type'}>{indicator.type}</p>
                        <p className={'indicator-name'}>{indicator.name}</p>
                        <Grid className={'quarter-selection-container'}>
                            <Button variant={'contained'} className={'quarter-selection'}>Q1</Button>
                            <Button variant={'contained'} className={'quarter-selection'}>Q2</Button>
                            <Button variant={'contained'} className={'quarter-selection'}>Q3</Button>
                            <Button variant={'contained'} className={'quarter-selection'}>Q4</Button>
                        </Grid>
                    </Card>
                </Grid>
            )
        })
    }

    renderProgrammes() {
        return this.state.programmes.map((programme) => {
            return (
                <Paper
                    className={'performance-indicators-container'}>
                    <div className={`IntroSection-text is-initialised ${this.state.open ? 'is-open' : ''}`}>
                        <div
                            className="IntroSection-content"
                        >
                            <p className={'programme-name'}>{programme.name}</p>
                            <Grid container spacing={3}>
                                {this.renderIndicatorCards(programme)}
                            </Grid>
                        </div>
                        {this.renderReadMoreButton()}
                    </div>
                </Paper>
            )
        })
    }

    render() {
        return (<div>{this.renderProgrammes()}</div>);
    }
}

class PerformanceIndicatorsContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (<div>
            <h3 className="Title Title--section">Indicators of performance</h3>
            <PerformanceIndicators/>
        </div>);
    }
}

function scripts() {
    const parent = document.getElementById('js-initPerformanceIndicators');
    if (parent) {
        ReactDOM.render(<PerformanceIndicatorsContainer
        />, parent)
    }
}


export default scripts();