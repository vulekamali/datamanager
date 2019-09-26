import sys
from tablib import Databook, Dataset


EXTRA_AGENT_HEADER = 'Other parties'
AGENT_HEADERS = ['Program Implementing Agent',
                 'Principal Agent',
                 'Main Contractor']
HEADERS = AGENT_HEADERS + [EXTRA_AGENT_HEADER]



class IRMReportSheet(object):
    def __init__(self, data_set):
        self.data_set = data_set
        self.output_data_set = self.create_output_data_set()
        self.contractor_columns = self._get_project_contractor_columns(
            data_set)

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
        for row in self.data_set:
            self.process_row(row)
        self.save_to_csv()

    def process_row(self, row):
        row_dict = {
            k: [] for k in HEADERS
        }
        empty_columns = 0
        for col in self.contractor_columns:
            cell = row[col]
            if not cell or len(cell.strip()) == 0:
                empty_columns += 1
                continue
            for agent_header in AGENT_HEADERS:
                if cell.lower().strip().startswith(agent_header.lower()):
                    agent_value = cell.split(':')[1].strip()
                    row_dict[agent_header].append(agent_value)
                    break
            else:
                # Agent hasn't been found, append to "Other parties"
                row_dict[EXTRA_AGENT_HEADER].append(cell)
        
        # Don't write empty rows to the output csv
        if empty_columns == len(self.contractor_columns):
            return

        self.output_data_set.append([
            '\n'.join(row_dict[k]) for k in HEADERS
        ])




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
