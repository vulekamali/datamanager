import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {
    FormControl,
    Grid, InputLabel, MenuItem, NativeSelect,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer, TableFooter,
    TableHead, TablePagination,
    TableRow
} from "@material-ui/core";
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";

class TabularView extends Component {
    constructor(props) {
        super(props);

        this.state = {
            rows: null,
            departments: null,
            financialYears: null,
            frequencies: null,
            governments: null,
            mtsfOutcomes: null,
            sectors: null,
            spheres: null,
            totalCount: 0,
            rowsPerPage: 0,
            currentPage: 0,
            selectedFilters: {}
        }
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchAPIData() {
        let url = `api/v1/eqprs/?page=${this.state.currentPage + 1}`;

        // append filters
        Object.keys(this.state.selectedFilters).forEach((key) => {
            let value = this.state.selectedFilters[key];
            if (value !== '') {
                url += `&${key}=${encodeURI(value)}`;
            }
        })

        fetchWrapper(url)
            .then((response) => {
                this.setState({
                    ...this.state,
                    rows: response.results.items,
                    departments: response.results.facets['department_name'],
                    financialYears: response.results.facets['financial_year_slug'],
                    frequencies: response.results.facets['frequency'],
                    governments: response.results.facets['government_name'],
                    mtsfOutcomes: response.results.facets['mtsf_outcome'],
                    sectors: response.results.facets['sector'],
                    spheres: response.results.facets['sphere_name'],
                    totalCount: response.count,
                    rowsPerPage: response.results.items.length
                });
            })
            .catch((errorResult) => console.warn(errorResult));
    }

    renderTableHead() {
        return (
            <TableRow>
                {Object.keys(this.state.rows[0]).map((key, index) => {
                    if (key !== 'id') {
                        return (<TableCell
                            key={index}
                            style={{borderRight: '1px solid #c6c6c6'}}
                        ><b>{key}</b></TableCell>)
                    }
                })}
            </TableRow>
        )
    }

    renderTableCells(row, index) {
        const isAlternating = index % 2 !== 0;
        return (
            <TableRow
                key={index}
            >
                {
                    Object.keys(row).map((key, i) => {
                        if (key !== 'id') {
                            return (
                                <TableCell
                                    key={`${index}_${i}`}
                                    style={{
                                        maxWidth: key === 'indicator_name' ? 250 : 150,
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        whiteSpace: "nowrap",
                                        backgroundColor: isAlternating ? '#f7f7f7' : '#fcfcfc',
                                        borderRight: '1px solid #c6c6c6'
                                    }}
                                    title={row[key]}
                                >{row[key]}</TableCell>
                            )
                        }
                    })
                }
            </TableRow>
        )
    }

    handlePageChange(event, newPage) {
        this.setState({
            ...this.state,
            currentPage: newPage
        }, () => {
            this.fetchAPIData();
        })
    }

    renderTable() {
        if (this.state.rows === null) {
            // todo : return loading state
            return <div></div>
        } else {
            return (
                <Paper>
                    <TableContainer style={{maxHeight: 440}}>
                        <Table stickyHeader aria-label="simple table" size={'small'}>
                            <TableHead>
                                {this.renderTableHead()}
                            </TableHead>
                            <TableBody>
                                {this.state.rows.map((row, index) => this.renderTableCells(row, index))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        colSpan={3}
                        count={this.state.totalCount}
                        rowsPerPage={this.state.rowsPerPage}
                        rowsPerPageOptions={[]}
                        page={this.state.currentPage}
                        onPageChange={(event, newPage) => this.handlePageChange(event, newPage)}
                        SelectProps={{
                            inputProps: {'aria-label': 'rows per page'},
                            native: true,
                        }}
                    />
                </Paper>
            )
        }
    }

    handleFilterChange(event) {
        const name = event.target.name;
        const value = event.target.value;

        let selectedFilters = this.state.selectedFilters;
        selectedFilters[name] = value;

        this.setState({
            ...this.state,
            currentPage: 0,
            selectedFilters: selectedFilters
        }, () => {
            this.fetchAPIData();
        })
    }

    renderDepartmentFilter() {
        if (this.state.departments === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-department'}>department</InputLabel>
                    <Select
                        native
                        label={'department'}
                        inputProps={{
                            id: 'frm-department',
                            name: 'department__name'
                        }}
                        value={this.state.selectedFilters['department__name']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.departments.map((department, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={department['department__name']}>
                                        {`${department['department__name']} (${department['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderFinancialYearFilter() {
        if (this.state.financialYears === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-financialYears'}>financial year</InputLabel>
                    <Select
                        native
                        label={'financial year'}
                        inputProps={{
                            id: 'frm-financialYears',
                            name: 'department__government__sphere__financial_year__slug'
                        }}
                        value={this.state.selectedFilters['department__government__sphere__financial_year__slug']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.financialYears.map((fy, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={fy['department__government__sphere__financial_year__slug']}>
                                        {`${fy['department__government__sphere__financial_year__slug']} (${fy['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderFrequencyFilter() {
        if (this.state.frequencies === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-frequency'}>frequency</InputLabel>
                    <Select
                        native
                        label={'frequency'}
                        inputProps={{
                            id: 'frm-frequency',
                            name: 'frequency'
                        }}
                        value={this.state.selectedFilters['frequency']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.frequencies.map((frequency, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={frequency['frequency']}>
                                        {`${frequency['frequency']} (${frequency['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderGovernmentFilter() {
        if (this.state.governments === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-government'}>government</InputLabel>
                    <Select
                        native
                        label={'government'}
                        inputProps={{
                            id: 'frm-government',
                            name: 'department__government__name'
                        }}
                        value={this.state.selectedFilters['department__government__name']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.governments.map((government, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={government['department__government__name']}>
                                        {`${government['department__government__name']} (${government['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderMtsfFilter() {
        if (this.state.mtsfOutcomes === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-mtsfOutcome'}>mtsf outcome</InputLabel>
                    <Select
                        native
                        label={'mtsf outcome'}
                        inputProps={{
                            id: 'frm-mtsfOutcome',
                            name: 'mtsf_outcome'
                        }}
                        value={this.state.selectedFilters['mtsf_outcome']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.mtsfOutcomes.map((mtsfOutcome, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={mtsfOutcome['mtsf_outcome']}>
                                        {`${mtsfOutcome['mtsf_outcome']} (${mtsfOutcome['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderSectorFilter() {
        if (this.state.sectors === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-sector'}>sector</InputLabel>
                    <Select
                        native
                        label={'sector'}
                        inputProps={{
                            id: 'frm-sector',
                            name: 'sector'
                        }}
                        value={this.state.selectedFilters['sector']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.sectors.map((sector, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={sector['sector']}>
                                        {`${sector['sector']} (${sector['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderSphereFilter() {
        if (this.state.spheres === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'}
                             style={{minWidth: '150px', maxWidth: '250px', marginLeft: '20px', marginTop: '10px', fontSize: '8px'}}>
                    <InputLabel htmlFor={'frm-sphere'}>sphere</InputLabel>
                    <Select
                        native
                        label={'sphere'}
                        inputProps={{
                            id: 'frm-sphere',
                            name: 'department__government__sphere__name'
                        }}
                        value={this.state.selectedFilters['department__government__sphere__name']}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                        <option aria-label={'None'} value={''}/>
                        {
                            this.state.spheres.map((sphere, index) => {
                                return (
                                    <option
                                        key={index}
                                        value={sphere['department__government__sphere__name']}>
                                        {`${sphere['department__government__sphere__name']} (${sphere['count']})`}
                                    </option>
                                )
                            })
                        }
                    </Select>
                </FormControl>
            )
        }
    }

    renderFilters() {
        return (
            <Grid container style={{marginBottom: '40px'}}>
                {this.renderDepartmentFilter()}
                {this.renderFinancialYearFilter()}
                {this.renderFrequencyFilter()}
                {this.renderGovernmentFilter()}
                {this.renderSectorFilter()}
                {this.renderMtsfFilter()}
                {this.renderSphereFilter()}
            </Grid>
        )
    }

    render() {
        return (
            <div>
                {this.renderFilters()}
                {this.renderTable()}
            </div>
        );
    }
}

function scripts() {
    const parent = document.getElementById('js-initTabularView');
    if (parent) {
      ReactDOM.render(
          <TabularView
          />, parent
      )
    }
}


export default scripts();
