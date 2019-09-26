"""
Script to parse the "Project Contractor" columns from a IRMReport xlsx sheet.

Run with:
```
python bin/provincial-infrastructure-projects.py 'input.xlsx' 'output.csv' --sheet_name 'IRMReport (30)'     
```
"""
import argparse
import sys
import os.path
from tablib import Databook, Dataset
from irm_report_headers import *


class IRMReportSheet(object):
    def __init__(self, data_set, output_path):
        self.data_set = data_set
        self.data_set_dict = data_set.dict
        self.output_path = output_path
        self.output_data_set = self.create_output_data_set()
        self.contractor_columns = self._get_project_contractor_columns(
            data_set)

    def _get_project_contractor_columns(self, data_set):
        headers = data_set.headers
        return [i for i in range(len(headers)) if headers[i].strip() == 'Project Contractor']

    def create_output_data_set(self):
        data = Dataset(title='provincial-infrastructure-projects')
        data.headers = HEADERS
        return data

    def save_to_csv(self):
        print('Saving data to csv...')
        with open(self.output_path, 'w') as output_file:
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


def get_IRM_report_data_set(input_file, sheet_name):
    print("Reading from file {}...".format(input_file))
    data_book = Databook().load('xlsx', open(input_file, 'rb').read())
    sheets = data_book.sheets()
    try:
        return next(data_set for data_set in sheets if data_set.title.strip() == sheet_name)
    except StopIteration:
        sys.exit('Sheet not found in xlsx file.')


def import_contractor_columns(input_file, output_path, sheet_name):
    report_sheet = IRMReportSheet(
        get_IRM_report_data_set(input_file, sheet_name), output_path)
    report_sheet.process()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='Path to input xlsx file')
    parser.add_argument('output_path', help='Path to output csv')
    parser.add_argument('--sheet_name',
                        help='Sheet in the xlsx file containing the IRM data',
                        default='IRMReport (30)')
    args = parser.parse_args()
    if not os.path.isfile(args.input_path):
        sys.exit('Input file does not exist.')

    import_contractor_columns(args.input_path, args.output_path, args.sheet_name)
