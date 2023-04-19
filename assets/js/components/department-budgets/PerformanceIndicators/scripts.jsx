import ReactDOM from "react-dom";
import React, {Component} from "react";
import Programme from "./programme";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            programmes: [{
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

    renderProgrammes() {
        return this.state.programmes.map((programme) => {
            return (
                <Programme
                    data={programme}
                />
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