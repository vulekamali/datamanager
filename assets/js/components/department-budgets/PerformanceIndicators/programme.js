import React, {Component} from "react";
import {Grid, Paper} from "@material-ui/core";
import IndicatorCard from "./indicator-card";

class Programme extends Component {
    constructor(props) {
        super(props);

        this.state = {
            open: false,
            triggered: false,
            programme: props.data
        }
    }

    setOpen() {
        this.setState({
            ...this.state, open: !this.state.open
        });
    }

    renderIndicatorCards(programme) {
        return programme.indicators.map((indicator) => {
            return (
                <IndicatorCard
                    data={indicator}
                />
            )
        })
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

    renderProgramme() {
        return (
            <Paper
                className={'performance-indicators-container'}>
                <div className={`IntroSection-text is-initialised ${this.state.open ? 'is-open' : ''}`}>
                    <div
                        className="IntroSection-content"
                    >
                        <p className={'programme-name'}>{this.state.programme.name}</p>
                        <Grid container spacing={3}>
                            {this.renderIndicatorCards(this.state.programme)}
                        </Grid>
                    </div>
                    {this.renderReadMoreButton()}
                </div>
            </Paper>
        )
    }

    render() {
        return (<div>{this.renderProgramme()}</div>);
    }
}

export default Programme;