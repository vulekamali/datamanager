import ReactDOM from "react-dom";
import React, {Component} from "react";
import Programme from "./programme";
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";
import decodeHtmlEntities from "../../../utilities/js/helpers/decodeHtmlEntities";
import {Button, CircularProgress, Dialog, Grid} from "@material-ui/core";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);

        this.state = {
            department: props.department,
            financialYear: props.year,
            sphere: props.sphere,
            government: props.government,
            previousYears: props.previousYears,
            programmes: [],
            previousYearsProgrammes: [],
            pageCount: 3,
            isLoading: true
        };
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchPreviousYearsAPIData() {
        this.state.previousYears.forEach((fy, index) => {
            this.fetchAPIDataRecursive(1, [], fy)
                .then((items) => {
                    let arr = this.state.previousYearsProgrammes;
                    arr[index] = {
                        financialYear: fy, programmes: this.extractProgrammeData(items)
                    }

                    this.setState({
                        ...this.state, previousYearsProgrammes: arr
                    });
                })
        })
    }

    fetchAPIData() {
        this.fetchAPIDataRecursive(1, [], this.state.financialYear)
            .then((items) => {
                this.setState({
                    ...this.state, isLoading: false, programmes: this.extractProgrammeData(items)
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
                name: p, visibleIndicators: allIndicators.slice(0, this.state.pageCount), allIndicators: allIndicators
            })
        })

        return data;
    }

    fetchAPIDataRecursive(page = 1, allItems = [], financialYear) {
        return new Promise((resolve, reject) => {
            const pageQuery = `page=${page}`;
            const departmentQuery = `department__name=${encodeURI(this.state.department)}`;
            const financialYearQuery = `department__government__sphere__financial_year__slug=${financialYear}`;
            const baseUrl = `../../../../../performance/api/v1/eqprs/`;
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
            ...this.state, programmes: programmes
        })
    }

    renderProgrammes() {
        if (this.state.programmes.length > 0) {
            return this.state.programmes.map((programme, index) => {
                let prevArr = this.state.previousYearsProgrammes.map(item => {
                    return {
                        financialYear: item.financialYear,
                        programme: item.programmes.filter(p => p.name === programme.name)[0]
                    };
                })

                return (<Programme
                    data={programme}
                    key={index}
                    showMore={() => this.handleShowMore(programme)}
                    previousYearsProgrammes={prevArr}
                    financialYear={this.state.financialYear}
                />)
            })
        } else {
            return (<div className="Message Message--secondary u-marginBottom60 ">
                <div className="Message-content">
                    <span className="Message-heading">Please note</span>
                </div>
                <div className="Message-text Message-text--secondary">No performance data currently available for this department.</div>
            </div>)
        }
    }

    renderLoadingState() {
        if (!this.state.isLoading) {
            return
        }
        const tableContainer = document.getElementsByClassName('js-initYearSelect')[0];
        const gifWidth = 40;
        const marginLeftVal = (tableContainer.clientWidth - gifWidth) / 2;

        return (<div className={'table-loading-state'} style={{height: '100px'}}>
            <CircularProgress
                className={'table-circular-progress'}
                style={{marginLeft: marginLeftVal, marginTop: '30px'}}
            />
        </div>)
    }

    render() {
        return (<div
            style={{position: 'relative'}}
        >
            {this.renderProgrammes()}
            {this.renderLoadingState()}
        </div>);
    }
}

class PerformanceIndicatorsContainer extends Component {
    constructor(props) {
        super(props);

        this.state = {
            dataDisclaimerAcknowledged: false,
            modalOpen: false,
            department: props.department,
            year: props.year,
            sphere: props.sphere,
            government: props.government,
            previousYears: props.previousYears
        }
    }

    componentDidMount() {
        this.checkForLocalStorage();
    }

    checkForLocalStorage() {
        const ack = localStorage.getItem('data-disclaimer-acknowledged');
        this.setState({
            ...this.state, dataDisclaimerAcknowledged: ack === 'true', modalOpen: ack !== 'true'
        })
    }

    handleStorage() {
        localStorage.setItem('data-disclaimer-acknowledged', 'true');
        this.setState({
            ...this.state, dataDisclaimerAcknowledged: true, modalOpen: false
        })
    }

    renderNavigateButtons() {
        const baseUrl = '../../../../../performance';
        const sphereQuery = `department__government__sphere__name=${encodeURI(this.state.sphere)}`;
        const governmentQuery = `department__government__name=${encodeURI(this.state.government)}`;
        const yearQuery = `department__government__sphere__financial_year__slug=${this.state.year}`;
        const departmentQuery = `department__name=${this.state.department}`;
        return (<Grid>
            <Button
                variant={'outlined'}
                className={'programme-btn'}
                href={`${baseUrl}/?${yearQuery}&${departmentQuery}&${sphereQuery}&${governmentQuery}`}
            >
                Search all performance indicators
            </Button>
            <Button
                variant={'outlined'}
                className={'programme-btn'}
                style={{marginLeft: '20px'}}
                href={'https://performance.vulekamali.gov.za/stages/implementation-monitoring#3.2'}
            >
                Learn more about quarterly performance reporting
            </Button>
        </Grid>)
    }

    renderModal() {
        return (<Dialog
            open={this.state.modalOpen}
            container={() => document.getElementById('js-initPerformanceIndicators')}
            style={{position: 'absolute'}}
            BackdropProps={{
                style: {position: 'absolute'}
            }}
            disableAutoFocus={true}
            disableEnforceFocus={true}
            className={'performance-modal'}
        >
            <Grid
                className={'performance-modal-title'}
            >
                Data disclaimer
            </Grid>
            <Grid
                className={'performance-modal-content'}
            >
                The Quarterly Performance Reporting (QPR) data (other than the Annual audited output field)
                is pre-audited non financial data. This data is approved by the accounting officer of the
                relevant organ of state before publication.
            </Grid>
            <Grid
                className={'performance-modal-link'}
            >
                <a
                    href="https://performance.vulekamali.gov.za/stages/implementation-monitoring#3.2"
                    target={'_blank'}
                >Learn more about these performance indicators.</a>
            </Grid>
            <Grid>
                <button
                    className={'Button is-inline u-marginBottom10 performance-modal-full performance-modal-button'}
                    onClick={() => this.handleStorage()}
                >
                    Acknowledge and continue
                </button>
            </Grid>
        </Dialog>)
    }

    render() {
        return (<div>
            <h3 className="Title Title--section">Indicators of performance</h3>
            <PerformanceIndicators
                department={this.state.department}
                year={this.state.year}
                government={this.state.government}
                sphere={this.state.sphere}
                previousYears={this.state.previousYears}
            />
            {this.renderNavigateButtons()}
            {this.renderModal()}
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
            previousYears.push(d.id)
        })
    }

    const parent = document.getElementById('js-initPerformanceIndicators');
    if (parent) {
        const departmentName = parent.getAttribute('data-department');
        const financialYear = parent.getAttribute('data-year');
        const sphere = parent.getAttribute('data-sphere');
        const government = parent.getAttribute('data-government');
        ReactDOM.render(<PerformanceIndicatorsContainer
            department={departmentName}
            year={financialYear}
            previousYears={previousYears}
            government={government}
            sphere={sphere}
        />, parent)
    }
}


export default scripts();