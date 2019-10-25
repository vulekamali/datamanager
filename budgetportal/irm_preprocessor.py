from tablib import Dataset


BASE_HEADERS = [
    "Project ID",
    "Project No",
    "Project Name",
    "Province",
    "Department",
    "Local Municipality",
    "District Municipality",
    "Latitude",
    "Longitude",
    "Project Status",
    "Project Start Date",
    "Estimated Construction Start Date",
    "Estimated Project Completion Date",
    "Contracted Construction End Date",
    "Estimated Construction End Date",
    "Professional Fees",
    "Construction Costs",
    "Variation Orders",
    "Total Project Cost",
    "Project Expenditure from Previous Financial Years (Professional Fees)",
    "Project Expenditure from Previous Financial Years (Construction Costs)",
    "Project Expenditure from Previous Financial Years (TOTAL)",
    "Main Budget Appropriation (Professional Fees)",
    "Adjustment Budget Appropriation (Professional Fees)",
    "Main Budget Appropriation (Construction Costs)",
    "Adjustment Budget Appropriation (Construction Costs)",
    "Main Budget Appropriation (TOTAL)",
    "Adjustment Budget Appropriation (TOTAL)",
    "Actual Expenditure Q1",
    "Actual Expenditure Q2",
    "Actual Expenditure Q3",
    "Actual Expenditure Q4",
    "Budget Programme",
    "Primary Funding Source",
    "Nature of Investment",
    "Funding Status",
]
EXTRA_IMPLEMENTOR_HEADER = "Other parties"
IMPLEMENTORS = ["Program Implementing Agent", "Principal Agent", "Main Contractor"]
IMPLEMENTOR_HEADERS = IMPLEMENTORS + [EXTRA_IMPLEMENTOR_HEADER]
OUTPUT_HEADERS = BASE_HEADERS + IMPLEMENTOR_HEADERS


class InputException(Exception):
    pass


def preprocess(input_dataset):
    """
    Given a tablib dataset with headers BASE_HEADERS and any number of coumns
    headed "Project Contractor", this returns a tablib dataset with headers
    BASE_HEADERS + IMPLEMENTOR_HEADERS + EXTRA_IMPLEMENTOR_HEADER where
    the "Project Contractor" columns have been transformed into the columns
    headed by IMPLEMENTOR_HEADERS + EXTRA_IMPLEMENTOR_HEADER
    """
    # We're going to assume things about the order of columns so ensure they're
    # in the order we expect.
    check_input_column_order(input_dataset.headers)
    output_dataset = Dataset(
        headers=BASE_HEADERS + IMPLEMENTOR_HEADERS + EXTRA_IMPLEMENTOR_HEADER
    )
    return output_dataset


def check_input_column_order(input_headers):
    for i, header in enumerate(input_headers):
        if i < len(BASE_HEADERS):
            expected_header = BASE_HEADERS[i]
            actual_header = input_headers[i]
        else:
            expected_header = "Project Contractor"
            actual_header = input_headers[i]
        if actual_header != expected_header:
            raise InputException(
                "Expected header %s in column %d but got %s"
                % (expected_header, i + 1, actual_header)
            )
