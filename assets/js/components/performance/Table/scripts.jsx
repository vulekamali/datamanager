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
    TableContainer,
    TableHead,
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
            selectedFilters: {}
        }
    }

    componentDidMount() {
        this.fetchAPIData();
    }

    fetchAPIData() {
        let url = 'api/v1/eqprs/';

        // append filters
        let firstParam = true;
        Object.keys(this.state.selectedFilters).forEach((key) => {
            let value = this.state.selectedFilters[key];
            if (value !== '') {
                url += firstParam ? '?' : '&';
                firstParam = false;
                url += `${key}=${value}`;
            }
        })
        console.log({url})

        fetchWrapper(url)
            .then((response) => {
                console.log({response})
                this.setState({
                    ...this.state,
                    rows: response.results.items,
                    departments: response.results.facets['department_name'],
                    financialYears: response.results.facets['financial_year_slug'],
                    frequencies: response.results.facets['frequency'],
                });
            })
            .catch((errorResult) => console.warn(errorResult));
    }

    renderTableHead() {
        return (
            <TableRow>
                {Object.keys(this.state.rows[0]).map((key) => {
                    return (<TableCell
                        style={{borderRight: '1px solid #c6c6c6'}}
                    ><b>{key}</b></TableCell>)
                })}
            </TableRow>
        )
    }

    renderTableCells(row, isAlternating) {
        return (
            <TableRow
                key={row.name}
            >
                {
                    Object.keys(row).map((key) => {
                        return (
                            <TableCell
                                style={{
                                    maxWidth: 150,
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    whiteSpace: "nowrap",
                                    backgroundColor: isAlternating ? '#f7f7f7' : '#fcfcfc',
                                    borderRight: '1px solid #c6c6c6'
                                }}
                                title={row[key]}
                            >{row[key]}</TableCell>
                        )
                    })
                }
            </TableRow>
        )
    }

    renderTable() {
        if (this.state.rows === null) {
            // todo : return loading state
            return <div></div>
        } else {
            return (
                <TableContainer component={Paper} style={{maxHeight: 440}}>
                    <Table stickyHeader aria-label="simple table" size={'small'}>
                        <TableHead>
                            {this.renderTableHead()}
                        </TableHead>
                        <TableBody>
                            {this.state.rows.map((row, index) => this.renderTableCells(row, index % 2 !== 0))}
                        </TableBody>
                    </Table>
                </TableContainer>
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
            selectedFilters: selectedFilters
        })

        this.fetchAPIData();
    }

    renderDepartmentFilter() {
        if (this.state.departments === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'} size={'small'} style={{minWidth: '150px', fontSize: '8px'}}>
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
                            this.state.departments.map((department) => {
                                return (
                                    <option
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
                             style={{minWidth: '150px', marginLeft: '20px', fontSize: '8px'}}>
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
                            this.state.financialYears.map((fy) => {
                                return (
                                    <option
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
                             style={{minWidth: '160px', marginLeft: '20px', fontSize: '8px'}}>
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
                            this.state.frequencies.map((frequency) => {
                                return (
                                    <option
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

    renderFilters() {
        return (
            <Grid container style={{marginBottom: '40px'}}>
                {this.renderDepartmentFilter()}
                {this.renderFinancialYearFilter()}
                {this.renderFrequencyFilter()}
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

    ReactDOM.render(
        <TabularView
        />, parent
    )
}


export default scripts();