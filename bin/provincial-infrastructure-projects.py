import sys
from tablib import Databook, Dataset
from irm_report_headers import *


class IRMReportSheet(object):
    def __init__(self, data_set):
        self.data_set = data_set
        self.data_set_dict = data_set.dict
        self.output_data_set = self.create_output_data_set()
        self.contractor_columns = self._get_project_contractor_columns(
            data_set)
        self.first_contractor_column = self.contractor_columns[0]

    def _get_project_contractor_columns(self, data_set):
        headers = data_set.headers
        return [i for i in range(len(headers)) if headers[i].strip() == 'Project Contractor']

    def create_output_data_set(self):
        data = Dataset(title='provincial-infrastructure-projects.csv')
        data.headers = HEADERS
        return data

    def save_to_csv(self):
        print('Saving data to csv...')
        with open('provincial-infrastructure-projects.csv', 'w') as output_file:
            output_file.write(self.output_data_set.export('csv'))

    def process(self):
        print("Processing data...")
        for i in range(len(self.data_set)):
            self.process_row(i)
        self.save_to_csv()

    def process_row(self, row_index):
        row = self.data_set[row_index]
        if is_empty_row(row):
            # Don't process empty rows
            return

        row_contractors = self.get_row_contractors(row)
        normal_cells = self.get_normal_cells(row_index)
        self.append_row_to_output_data_set(normal_cells + row_contractors)

    def get_normal_cells(self, row_index):
        row = self.data_set_dict[row_index]
        return [row[header] for header in NORMAL_HEADERS]

    def get_row_contractors(self, row):
        row_contractors = {
            k: [] for k in AGENT_HEADERS
        }
        for col in self.contractor_columns:
            cell = row[col]
            if is_empty_cell(cell):
                continue
            for agent_header in AGENTS:
                if cell.lower().strip().startswith(agent_header.lower()):
                    agent_value = cell.split(':')[1].strip()
                    row_contractors[agent_header].append(agent_value)
                    break
            else:
                # Agent hasn't been found, append to "Other parties"
                row_contractors[EXTRA_AGENT_HEADER].append(cell)

        return [
            '\n'.join(row_contractors[k]) for k in AGENT_HEADERS
        ]

    def append_row_to_output_data_set(self, row_data):
        self.output_data_set.append(row_data)


def is_empty_cell(cell):
    return not cell or (isinstance(cell, basestring) and len(cell.strip()) == 0)


def is_not_empty_cell(cell):
    return not is_empty_cell(cell)


def is_empty_row(row):
    return len(list(filter(is_not_empty_cell, row))) == 0


def get_IRM_report_data_set(input_file):
    print("Reading from file {}...".format(input_file))
    data_book = Databook().load(
        'xlsx',
        open(input_file, 'rb').read())
    sheets = data_book.sheets()
    # TODO: select sheet by name
    return sheets[1]


def import_contractor_columns(input_file):
    report_sheet = IRMReportSheet(get_IRM_report_data_set(input_file))
    report_sheet.process()


if __name__ == "__main__":
    input_file = "bin/20190722_proposed_IRM_field.xlsx"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    import_contractor_columns(input_file)
