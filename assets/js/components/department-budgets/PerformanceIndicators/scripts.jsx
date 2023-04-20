import ReactDOM from "react-dom";
import React, {Component} from "react";
import Programme from "./programme";
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            department: props.department,
            programmes: []
        };
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchAPIData() {
        let url = `../../../../performance/api/v1/eqprs/?page=1&department__name=` + encodeURI(this.state.department);

        fetchWrapper(url)
            .then((response) => {
                let programmes = [...new Set(response.results.items.map(x => x.programme_name))];
                let data = [];
                programmes.forEach(p => {
                    data.push({
                        name: p,
                        indicators: response.results.items.filter(x => x.programme_name === p).slice(0, 3)
                    })
                })
                this.setState({
                    ...this.state,
                    programmes: data
                });

                console.log({data})
            })
            .catch((errorResult) => console.warn(errorResult));
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

        this.state = {
            department: props.department
        }
    }

    render() {
        return (<div>
            <h3 className="Title Title--section">Indicators of performance</h3>
            <PerformanceIndicators
                department={this.state.department}
            />
        </div>);
    }
}

function scripts() {
    const parent = document.getElementById('js-initPerformanceIndicators');
    if (parent) {
        const departmentName = parent.getAttribute('data-department');
        ReactDOM.render(<PerformanceIndicatorsContainer
            department={departmentName}
        />, parent)
    }
}


export default scripts();