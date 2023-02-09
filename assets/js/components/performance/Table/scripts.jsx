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

    renderFilter(id, apiField, stateField, fieldLabel, blankLabel) {
        if (this.state[stateField] === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'}
                             size={'small'}
                             style={{minWidth: '150px',
                                     maxWidth: '250px',
                                     marginRight: '10px',
                                     marginTop: '15px',
                                     fontSize: '8px'}}>
                    <InputLabel htmlFor={`frm-${id}`} shrink>{ fieldLabel }</InputLabel>
                    <Select
                        native
                        notched
                        label={fieldLabel}
                        inputProps={{
                            id: `frm-${id}`,
                            name: apiField
                        }}
                        value={this.state.selectedFilters[apiField]}
                        onChange={(event) => this.handleFilterChange(event)}
                    >
                      <option aria-label={blankLabel} value={''}>{blankLabel}</option>
                      {
                          this.state[stateField].map((option, index) => {
                              return (
                                  <option
                                    key={index}
                                    value={option[apiField]}>
                                    {`${option[apiField]} (${option['count']})`}
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
                {this.renderFilter('financialYears',
                                   'department__government__sphere__financial_year__slug',
                                   'financialYears',
                                   'Financial year',
                                   'All financial years')}
                {this.renderFilter('sphere',
                                   'department__government__sphere__name',
                                   'spheres',
                                   'Sphere',
                                   'All spheres')}
                {this.renderFilter('government',
                                   'department__government__name',
                                   'governments',
                                   'Government',
                                   'All governments')}
                {this.renderFilter('department',
                                   'department__name',
                                   'departments',
                                   'Department',
                                   'All departments')}
                {this.renderFilter('frequency',
                                   'frequency',
                                   'frequencies',
                                   'Frequency',
                                   'All frequencies')}
                {this.renderFilter('sector',
                                   'sector',
                                   'sectors',
                                   'Sectors',
                                   'All sectors')}
                {this.renderFilter('mtsfOutcome',
                                   'mtsf_outcome',
                                   'mtsfOutcomes',
                                   'MTSF Outcome',
                                   'All outcomes')}
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
