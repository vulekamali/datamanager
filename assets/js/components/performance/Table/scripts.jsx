import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {
    FormControl,
    Grid, InputLabel, MenuItem,
    TextField,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer, TableFooter,
    TableHead, TablePagination,
    TableRow
} from "@material-ui/core";
import {ThemeProvider} from "@material-ui/styles";
import {createTheme} from '@material-ui/core/styles';
import fetchWrapper from "../../../utilities/js/helpers/fetchWrapper";
import debounce from "lodash.debounce";

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
            selectedFilters: {},
            excludeColumns: new Set(['id', 'department']),
            titleMappings: {
                'indicator_name': 'Indicator name',
                'q1_target': 'Quarter 1 target',
                'q1_actual_output': 'Quarter 1 actual output',
                'q1_deviation_reason': 'Quarter 1 deviation reason',
                'q1_corrective_action': 'Quarter 1 corrective action',
                'q2_target': 'Quarter 2 target',
                'q2_actual_output': 'Quarter 2 actual output',
                'q2_deviation_reason': 'Quarter 2 deviation reason',
                'q2_corrective_action': 'Quarter 2 corrective action',
                'q3_target': 'Quarter 3 target',
                'q3_actual_output': 'Quarter 3 actual output',
                'q3_deviation_reason': 'Quarter 3 deviation reason',
                'q3_corrective_action': 'Quarter 3 corrective action',
                'q4_target': 'Quarter 4 target',
                'q4_actual_output': 'Quarter 4 actual output',
                'q4_deviation_reason': 'Quarter 4 deviation reason',
                'q4_corrective_action': 'Quarter 4 corrective action',
                'annual_target': 'Annual target',
                'annual_aggregate_output': 'Annual aggregate output',
                'annual_pre_audit_output': 'Annual pre-audit output',
                'annual_deviation_reason': 'Annual deviation reason',
                'annual_corrective_action': 'Annual corrective action',
                'annual_audited_output': 'Annual audited output',
                'sector': 'Sector',
                'programme_name': 'Programme name',
                'subprogramme_name': 'Subprogramme name',
                'frequency': 'Frequency',
                'type': 'Type',
                'subtype': 'Subtype',
                'mtsf_outcome': 'Mtsf outcome',
                'cluster': 'Cluster',
                'financial_year': 'Financial year',
                'department_name': 'Department name',
                'government_name': 'Government name',
                'sphere_name': 'Sphere name'
            }
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
        const includeColumns = ["financial_year", "department_name", "government_name", "sphere_name"];
        if (this.state.rows.length > 0) {
            return (
                <TableRow>
                    {Object.keys(this.state.rows[0]).map((key, index) => {
                        if (!this.state.excludeColumns.has(key)) {
                            return (<TableCell
                                key={index}
                                style={{borderRight: '1px solid #c6c6c6'}}
                            ><b>{this.getTitleMapping(key)}</b></TableCell>)
                        }
                    })}
                    {includeColumns.map((key, index) => {
                        return (<TableCell
                            key={index}
                            style={{borderRight: '1px solid #c6c6c6'}}
                        ><b>{this.getTitleMapping(key)}</b></TableCell>)
                    })}
                </TableRow>
            )
        } else {
            return <div>No matching indicators found.</div>;
        }
    }

    getTitleMapping(key) {
        const mapping = this.state.titleMappings[key];

        return mapping === undefined ? key : mapping;
    }

    renderTableCells(row, index) {
        const includeColumns = [row.department.government.sphere.financial_year.slug, row.department.name, row.department.government.name, row.department.government.sphere.name];
        const isAlternating = index % 2 !== 0;
        return (
            <TableRow
                key={index}
            >
                {
                    Object.keys(row).map((key, i) => {
                        if (!this.state.excludeColumns.has(key)) {
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
                {
                    includeColumns.map((value, i) => {
                        return (
                            <TableCell
                                key={i}
                                style={{
                                    maxWidth: 150,
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    whiteSpace: "nowrap",
                                    backgroundColor: isAlternating ? '#f7f7f7' : '#fcfcfc',
                                    borderRight: '1px solid #c6c6c6'
                                }}
                                title={value}
                            >{value}</TableCell>
                        )
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

    renderPagination() {
        return (
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
                component="div"
            />
        );
    }

    renderTable() {
        if (this.state.rows === null) {
            // todo : return loading state
            return <div></div>
        } else {
            const tableTheme = createTheme({
                overrides: {
                    MuiTablePagination: {
                        spacer: {
                            flex: 'none'
                        },
                        toolbar: {
                            "padding-left": "16px"
                        }
                    }
                }
            });
            return (
                <ThemeProvider theme={tableTheme}>
                    {this.renderPagination()}
                    <Paper>
                        <TableContainer>
                            <Table stickyHeader aria-label="simple table" size={'small'}>
                                <TableHead>
                                    {this.renderTableHead()}
                                </TableHead>
                                <TableBody>
                                    {this.state.rows.map((row, index) => this.renderTableCells(row, index))}
                                </TableBody>
                                <TableFooter>
                                    <TableRow>
                                    </TableRow>
                                </TableFooter>
                            </Table>
                        </TableContainer>
                    </Paper>
                    {this.renderPagination()}
                </ThemeProvider>
            );
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

    renderSearchField() {
        const debouncedHandleFilterChange = debounce((event) => this.handleFilterChange(event), 300);
        const persistedEventDeboundedHandler = (event) => {
            // https://reactjs.org/docs/legacy-event-pooling.html
            event.persist();
            debouncedHandleFilterChange(event);
        };

        return (
            <FormControl variant={'outlined'}
                         size={'small'}
                         style={{
                             marginRight: '10px',
                             marginTop: '15px',
                             fontSize: '8px'
                         }}>
                <TextField variant="outlined"
                           size="small"
                           label="Search indicators"
                           inputProps={{
                               id: "frm-textSearch",
                               name: "q"
                           }}
                           onChange={persistedEventDeboundedHandler}/>
            </FormControl>
        )
    }

    renderFilter(id, apiField, stateField, fieldLabel, blankLabel) {
        if (this.state[stateField] === null) {
            return <div></div>
        } else {
            return (
                <FormControl variant={'outlined'}
                             size={'small'}
                             style={{
                                 minWidth: '150px',
                                 maxWidth: '250px',
                                 marginRight: '10px',
                                 marginTop: '15px',
                                 fontSize: '8px'
                             }}>
                    <InputLabel htmlFor={`frm-${id}`} shrink>{fieldLabel}</InputLabel>
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
            <Grid container>
                {this.renderSearchField()}
                {this.renderFilter(
                    'financialYears',
                    'department__government__sphere__financial_year__slug',
                    'financialYears',
                    'Financial year',
                    'All financial years'
                )}
                {this.renderFilter(
                    'sphere',
                    'department__government__sphere__name',
                    'spheres',
                    'Sphere',
                    'All spheres'
                )}
                {this.renderFilter(
                    'government',
                    'department__government__name',
                    'governments',
                    'Government',
                    'All governments'
                )}
                {this.renderFilter(
                    'department',
                    'department__name',
                    'departments',
                    'Department',
                    'All departments'
                )}
                {this.renderFilter(
                    'frequency',
                    'frequency',
                    'frequencies',
                    'Frequency',
                    'All frequencies'
                )}
                {this.renderFilter(
                    'sector',
                    'sector',
                    'sectors',
                    'Sectors',
                    'All sectors'
                )}
                {this.renderFilter(
                    'mtsfOutcome',
                    'mtsf_outcome',
                    'mtsfOutcomes',
                    'MTSF Outcome',
                    'All outcomes'
                )}
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
