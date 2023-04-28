import ReactDOM from "react-dom";
import React, {Component} from "react";
import Programme from "./programme";
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";
import decodeHtmlEntities from "../../../utilities/js/helpers/decodeHtmlEntities";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            department: props.department,
            financialYear: props.year,
            previousYears: props.previousYears,
            programmes: [],
            previousYearsProgrammes: [],
            pageCount: 3
        };
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchPreviousYearsAPIData() {
        this.state.previousYears.forEach((fy) => {
            this.fetchAPIDataRecursive(1, [], fy)
                .then((items) => {
                    let arr = this.state.previousYearsProgrammes;
                    arr.push({
                        financialYear: fy,
                        programmes: this.extractProgrammeData(items)
                    })

                    this.setState({
                        ...this.state,
                        previousYearsProgrammes: arr
                    });
                })
        })
    }

    fetchAPIData() {
        this.fetchAPIDataRecursive(1, [], this.state.financialYear)
            .then((items) => {
                this.setState({
                    ...this.state,
                    programmes: this.extractProgrammeData(items)
                });

                this.fetchPreviousYearsAPIData();
            })
    }

    extractProgrammeData(items) {
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

        return data;
    }

    fetchAPIDataRecursive(page = 1, allItems = [], financialYear) {
        return new Promise((resolve, reject) => {
            const pageQuery = `page=${page}`;
            const departmentQuery = `department__name=${encodeURI(this.state.department)}`;
            const financialYearQuery = `department__government__sphere__financial_year__slug=${financialYear}`;
            const baseUrl = `../../../../performance/api/v1/eqprs/`;
            let url = `${baseUrl}?${pageQuery}&${departmentQuery}&${financialYearQuery}`;

            fetchWrapper(url)
                .then((response) => {
                    let newArr = allItems.concat(response.results.items);
                    if (response.next === null) {
                        resolve(newArr);
                    } else {
                        this.fetchAPIDataRecursive(page + 1, newArr, financialYear)
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
        return this.state.programmes.map((programme, index) => {
            let prevArr = this.state.previousYearsProgrammes.map(item => {
                return {
                    financialYear: item.financialYear,
                    programme: item.programmes.filter(p => p.name === programme.name)[0]
                };
            })

            return (
                <Programme
                    data={programme}
                    key={index}
                    showMore={() => this.handleShowMore(programme)}
                    previousYearsProgrammes={prevArr}
                    financialYear={this.state.financialYear}
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
            department: props.department,
            year: props.year,
            previousYears: props.previousYears
        }
    }

    render() {
        return (<div>
            <h3 className="Title Title--section">Indicators of performance</h3>
            <PerformanceIndicators
                department={this.state.department}
                year={this.state.year}
                previousYears={this.state.previousYears}
            />
        </div>);
    }
}

function scripts() {
    const nodes = document.getElementsByClassName('js-initYearSelect');
    const nodesArray = [...nodes];
    let previousYears = [];

    if (nodesArray.length > 0) {
        const jsonData = JSON.parse(decodeHtmlEntities(nodes[0].getAttribute('data-json'))).data;
        jsonData.forEach((d) => {
            if (!d.is_selected) {
                previousYears.push(d.id)
            }
        })
    }

    const parent = document.getElementById('js-initPerformanceIndicators');
    if (parent) {
        const departmentName = parent.getAttribute('data-department');
        const financialYear = parent.getAttribute('data-year');
        ReactDOM.render(<PerformanceIndicatorsContainer
            department={departmentName}
            year={financialYear}
            previousYears={previousYears}
        />, parent)
    }
}


export default scripts();