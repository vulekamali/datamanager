import ReactDOM from "react-dom";
import React, {Component} from "react";
import Programme from "./programme";
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            department: props.department,
            programmes: [],
            pageCount: 3
        };
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchAPIData() {
        this.fetchAPIDataRecursive(1, [])
            .then((items) => {
                console.log({items})
                let programmes = [...new Set(items.map(x => x.programme_name))];
                let data = [];
                programmes.forEach(p => {
                    const allIndicators = items.filter(x => x.programme_name === p);
                    data.push({
                        name: p,
                        visibleIndicators: allIndicators.slice(0, this.state.pageCount),
                        allIndicators: allIndicators
                    })
                })
                this.setState({
                    ...this.state,
                    programmes: data
                });
            })
    }

    fetchAPIDataRecursive(page = 1, allItems = []) {
        return new Promise((resolve, reject) => {
            let url = `../../../../performance/api/v1/eqprs/?page=${page}&department__name=` + encodeURI(this.state.department);

            fetchWrapper(url)
                .then((response) => {
                    let newArr = allItems.concat(response.results.items);
                    if (response.next === null) {
                        resolve(newArr);
                    } else {
                        this.fetchAPIDataRecursive(page + 1, newArr)
                            .then((items) => {
                                resolve(items);
                            });
                    }
                })
                .catch((errorResult) => console.warn(errorResult));
        })
    }

    handleShowMore(currentProgramme) {
        let programmes = this.state.programmes.map(programme => {
            if (programme.name === currentProgramme.name) {
                programme.visibleIndicators = programme.allIndicators.slice(0, programme.visibleIndicators.length + this.state.pageCount);
            }
            return programme;
        })

        this.setState({
            ...this.state,
            programmes: programmes
        })
    }

    renderProgrammes() {
        return this.state.programmes.map((programme) => {
            return (
                <Programme
                    data={programme}
                    showMore={() => this.handleShowMore(programme)}
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