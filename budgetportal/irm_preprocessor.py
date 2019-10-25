from tablib import Dataset


BASE_HEADERS = [
    u"Project ID",
    u"Project No",
    u"Project Name",
    u"Province",
    u"Department",
    u"Local Municipality",
    u"District Municipality",
    u"Latitude",
    u"Longitude",
    u"Project Status",
    u"Project Start Date",
    u"Estimated Construction Start Date",
    u"Estimated Project Completion Date",
    u"Contracted Construction End Date",
    u"Estimated Construction End Date",
    u"Professional Fees",
    u"Construction Costs",
    u"Variation Orders",
    u"Total Project Cost",
    u"Project Expenditure from Previous Financial Years (Professional Fees)",
    u"Project Expenditure from Previous Financial Years (Construction Costs)",
    u"Project Expenditure from Previous Financial Years (TOTAL)",
    u"Project Expenditure (TOTAL)",
    u"Main Budget Appropriation (Professional Fees)",
    u"Adjustment Budget Appropriation (Professional Fees)",
    u"Main Budget Appropriation (Construction Costs)",
    u"Adjustment Budget Appropriation (Construction Costs)",
    u"Main Budget Appropriation (TOTAL)",
    u"Adjustment Budget Appropriation (TOTAL)",
    u"Actual Expenditure Q1",
    u"Actual Expenditure Q2",
    u"Actual Expenditure Q3",
    u"Actual Expenditure Q4",
    u"Budget Programme",
    u"Primary Funding Source",
    u"Nature of Investment",
    u"Funding Status",
]
REPEATED_IMPLEMENTOR_HEADER = u"Project Contractor"
EXTRA_IMPLEMENTOR_HEADER = "Other parties"
IMPLEMENTORS = [u"Program Implementing Agent", u"Principal Agent", u"Main Contractor"]
IMPLEMENTOR_HEADERS = IMPLEMENTORS + [EXTRA_IMPLEMENTOR_HEADER]
OUTPUT_HEADERS = BASE_HEADERS + IMPLEMENTOR_HEADERS


class InputException(Exception):
    pass


def preprocess(input_dataset):
    """
    Given a tablib dataset with headers BASE_HEADERS and any number of coumns
    headed REPEATED_IMPLEMENTOR_HEADER, this returns a tablib dataset with headers
    BASE_HEADERS + IMPLEMENTOR_HEADERS + EXTRA_IMPLEMENTOR_HEADER where
    the REPEATED_IMPLEMENTOR_HEADER columns have been transformed into the columns
    headed by IMPLEMENTOR_HEADERS + EXTRA_IMPLEMENTOR_HEADER
    """
    # We're going to assume things about the order of columns so ensure they're
    # in the order we expect.
    check_input_column_order(input_dataset.headers)
    implementor_column_indexes = get_implementor_column_indexes(input_dataset.headers)
    output_dataset = Dataset(headers=BASE_HEADERS + IMPLEMENTOR_HEADERS)
    for row in input_dataset:
        output_dataset.append(preprocess_row(row, implementor_column_indexes))
    return output_dataset


def check_input_column_order(input_headers):
    for i, header in enumerate(input_headers):
        if i < len(BASE_HEADERS):
            expected_header = BASE_HEADERS[i]
            actual_header = input_headers[i]
        else:
            expected_header = REPEATED_IMPLEMENTOR_HEADER
            actual_header = input_headers[i]
        if actual_header != expected_header:
            raise InputException(
                "Expected header %s in column %d but got %s"
                % (expected_header, i + 1, actual_header)
            )


def get_implementor_column_indexes(headers):
    return [
        i
        for i in range(len(headers))
        if headers[i].strip() == REPEATED_IMPLEMENTOR_HEADER
    ]


def preprocess_row(row, implementor_column_indexes):
    base_columns = list(row[: len(BASE_HEADERS)])
    implementor_columns = get_row_implementors(row, implementor_column_indexes)
    return base_columns + implementor_columns


def get_row_implementors(row, implementor_column_indexes):
    prefixes = {header.lower() + ":": header for header in IMPLEMENTOR_HEADERS}
    row_implementors = {header: [] for header in IMPLEMENTOR_HEADERS}
    for col in implementor_column_indexes:
        cell = row[col]
        if cell is not None and cell.strip():
            for prefix in prefixes:
                if cell.lower().strip().startswith(prefix):
                    implementor_value = cell.split(":")[1].strip()
                    row_implementors[prefixes[prefix]].append(implementor_value)
                    break
            else:

                # Implementor hasn't been found, append to "Other parties"
                row_implementors[EXTRA_IMPLEMENTOR_HEADER].append(cell)

    return ["\n".join(row_implementors[k]) for k in IMPLEMENTOR_HEADERS]
