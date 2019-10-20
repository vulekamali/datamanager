from tablib import Dataset


NORMAL_HEADERS = [
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
EXTRA_AGENT_HEADER = "Other parties"
AGENTS = ["Program Implementing Agent", "Principal Agent", "Main Contractor"]
AGENT_HEADERS = AGENTS + [EXTRA_AGENT_HEADER]
HEADERS = NORMAL_HEADERS + AGENT_HEADERS


class IRMReportSheet(object):
    def __init__(self, data_set):
        self.data_set = data_set
        self.data_set_dict = data_set.dict
        self.output_data_set = self.create_output_data_set()
        self.contractor_columns = self._get_project_contractor_columns(data_set)

    @staticmethod
    def _get_project_contractor_columns(data_set):
        headers = data_set.headers
        return [
            i for i in range(len(headers)) if headers[i].strip() == "Project Contractor"
        ]

    @staticmethod
    def create_output_data_set():
        data = Dataset(title="provincial-infrastructure-projects")
        data.headers = AGENT_HEADERS
        return data

    def process(self):
        for i in range(len(self.data_set)):
            self.process_row(i)

    def process_row(self, row_index):
        row = self.data_set[row_index]
        if is_empty_row(row):
            return

        row_contractors = self.get_row_contractors(row)
        # empty strings should converted into null
        for index, row in enumerate(row_contractors):
            if row == "":
                row_contractors[index] = None
        self.append_row_to_output_data_set(row_contractors)

    def append_row_to_output_data_set(self, row_data):
        self.output_data_set.append(row_data)

    def get_row_contractors(self, row):
        row_contractors = {k: [] for k in AGENT_HEADERS}
        for col in self.contractor_columns:
            cell = row[col]
            if is_empty_cell(cell):
                continue
            for agent_header in AGENTS:
                if cell.lower().strip().startswith(agent_header.lower()):
                    agent_value = cell.split(":")[1].strip()
                    row_contractors[agent_header].append(agent_value)
                    break
            else:
                # Agent hasn't been found, append to "Other parties"
                row_contractors[EXTRA_AGENT_HEADER].append(cell)

        return ["\n".join(row_contractors[k]) for k in AGENT_HEADERS]


def is_empty_cell(cell):
    return not cell or (isinstance(cell, basestring) and len(cell.strip()) == 0)


def is_not_empty_cell(cell):
    return not is_empty_cell(cell)


def is_empty_row(row):
    return len(list(filter(is_not_empty_cell, row))) == 0
