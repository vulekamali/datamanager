from tablib import Databook, Dataset


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




class ProvInfraProjectSnapshotImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import provincial infrastructure projects.
    """

    financial_year = forms.ModelChoiceField(
        queryset=FinancialYear.objects.all(), required=True
    )


class ProvInfraProjectSnapshotLoader(ModelInstanceLoader):
    def get_instance(self, row):
        """
        Gets a Provincial Infrastructure project instance by IRM_project_id.
        """
        project_id = self.resource.fields["IRM_project_id"].clean(row)

        try:
            return ProvInfraProjectSnapshot.objects.get(IRM_project_id=project_id)
        except ProvInfraProjectSnapshot.DoesNotExist:
            pass

        return None


class ProvInfraProjectSnapshotResource(resources.ModelResource):
    IRM_project_id = Field(attribute="IRM_project_id", column_name="Project ID")
    project_number = Field(attribute="project_number", column_name="Project No")
    name = Field(attribute="name", column_name="Project Name")
    province = Field(attribute="province", column_name="Province")
    department = Field(attribute="department", column_name="Department")
    local_municipality = Field(
        attribute="local_municipality", column_name="Local Municipality"
    )
    district_municipality = Field(
        attribute="district_municipality", column_name="District Municipality"
    )
    latitude = Field(attribute="latitude", column_name="Latitude")
    longitude = Field(attribute="longitude", column_name="Longitude")
    status = Field(attribute="status", column_name="Project Status")
    start_date = Field(attribute="start_date", column_name="Project Start Date")
    estimated_construction_start_date = Field(
        attribute="estimated_construction_start_date",
        column_name="Estimated Construction Start Date",
    )
    estimated_completion_date = Field(
        attribute="estimated_completion_date",
        column_name="Estimated Project Completion Date",
    )
    contracted_construction_end_date = Field(
        attribute="contracted_construction_end_date",
        column_name="Contracted Construction End Date",
    )
    estimated_constructtion_end_date = Field(
        attribute="estimated_construction_end_date",
        column_name="Estimated Construction End Date",
    )
    total_professional_fees = Field(
        attribute="total_professional_fees", column_name="Professional Fees"
    )
    total_construction_costs = Field(
        attribute="total_construction_costs", column_name="Construction Costs"
    )
    variation_orders = Field(
        attribute="variation_orders", column_name="Variation Orders"
    )
    total_project_cost = Field(
        attribute="total_project_cost", column_name="Total Project Cost"
    )
    expenditure_from_previous_years_professional_fees = Field(
        attribute="expenditure_from_previous_years_professional_fees",
        column_name="Project Expenditure from Previous Financial Years (Professional Fees)",
    )
    expenditure_from_previous_years_construction_costs = Field(
        attribute="expenditure_from_previous_years_construction_costs",
        column_name="Project Expenditure from Previous Financial Years (Construction Costs)",
    )
    expenditure_from_previous_years_total = Field(
        attribute="expenditure_from_previous_years_total",
        column_name="Project Expenditure from Previous Financial Years (TOTAL)",
    )
    project_expenditure_total = Field(
        attribute="project_expenditure_total", column_name="Project Expenditure (TOTAL)"
    )
    main_appropriation_professional_fees = Field(
        attribute="main_appropriation_professional_fees",
        column_name="Main Budget Appropriation (Professional Fees)",
    )
    adjustment_appropriation_professional_fees = Field(
        attribute="adjustment_appropriation_professional_fees",
        column_name="Adjustment Budget Appropriation (Professional Fees)",
    )
    main_appropriation_construction_costs = Field(
        attribute="main_appropriation_construction_costs",
        column_name="Main Budget Appropriation (Construction Costs)",
    )
    adjustment_appropriation_construction_costs = Field(
        attribute="adjustment_appropriation_construction_costs",
        column_name="Adjustment Budget Appropriation (Construction Costs)",
    )
    main_appropriation_total = Field(
        attribute="main_appropriation_total",
        column_name="Main Budget Appropriation (TOTAL)",
    )
    adjustment_appropriation_total = Field(
        attribute="adjustment_appropriation_total",
        column_name="Adjustment Budget Appropriation (TOTAL)",
    )
    actual_expenditure_q1 = Field(
        attribute="actual_expenditure_q1", column_name="Actual Expenditure Q1"
    )
    actual_expenditure_q2 = Field(
        attribute="actual_expenditure_q2", column_name="Actual Expenditure Q2"
    )
    actual_expenditure_q3 = Field(
        attribute="actual_expenditure_q3", column_name="Actual Expenditure Q3"
    )
    actual_expenditure_q4 = Field(
        attribute="actual_expenditure_q4", column_name="Actual Expenditure Q4"
    )
    budget_programme = Field(
        attribute="budget_programme", column_name="Budget Programme"
    )
    primary_funding_source = Field(
        attribute="primary_funding_source", column_name="Primary Funding Source"
    )
    nature_of_investment = Field(
        attribute="nature_of_investment", column_name="Nature of Investment"
    )
    funding_status = Field(attribute="funding_status", column_name="Funding Status")
    program_implementing_agent = Field(
        attribute="program_implementing_agent", column_name="Program Implementing Agent"
    )
    principle_agent = Field(attribute="principle_agent", column_name="Principal Agent")
    main_contractor = Field(attribute="main_contractor", column_name="Main Contractor")
    other_parties = Field(attribute="other_parties", column_name="Other parties")
    financial_year = Field(
        attribute="financial_year",
        column_name="Financial Year",
        widget=ForeignKeyWidget(FinancialYear),
    )

    class Meta:
        model = ProvInfraProjectSnapshot
        skip_unchanged = True
        report_skipped = False
        exclude = ("id",)
        instance_loader_class = ProvInfraProjectSnapshotLoader

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        headers = dataset.headers

        # Check if the headers of the dataset and the specified headers are
        # the same or not. If not, raise exception with the missing headers
        difference = list(set(NORMAL_HEADERS) - set(headers))
        if len(difference) != 0:
            raise Exception(
                "Following column(s) are missing: {}".format(", ".join(difference))
            )

        # IRMReportSheet class processes the dataset and saves the processed
        # dataset in it's output_data_set attribute
        report_sheet = IRMReportSheet(dataset)
        report_sheet.process()

        # During process, empty rows must be deleted first from the dataset
        # the following code checks whether number of rows are the same for
        # the given dataset and the output dataset. If not, raises exception
        num_of_rows_dataset = report_sheet.data_set.height
        num_of_rows_output_dataset = report_sheet.output_data_set.height
        if num_of_rows_dataset != num_of_rows_output_dataset:
            raise Exception(
                "Number of rows in dataset({0}) don't match with the number of rows in the output dataset({1})!".format(
                    num_of_rows_dataset, num_of_rows_output_dataset
                )
            )

        # Following loops delete contractor columns and append mapped
        # agent/contractor/parties columns respectively
        for header in reversed(report_sheet.contractor_columns):
            del dataset[dataset.headers[header]]
        for agent in AGENT_HEADERS:
            dataset.append_col(report_sheet.output_data_set[agent], header=agent)

        # import_data() works with 2 requests, first one is import form request
        # and the second one is confirm import form request. Since user selects
        # financial year in import form request, it should be carried for
        # the second request.
        financial_year = self.request.POST.get("financial_year", None)
        if financial_year:
            self.request.session["import_context_year"] = financial_year
        else:
            # if it's confirm form request,it takes the selected financial year
            # value from import form request using django sessions
            try:
                financial_year = self.request.session["import_context_year"]
            except KeyError as e:
                raise Exception(
                    "Financial year context failure on row import, "
                    + "check resources.py for more info: {0}".format(e)
                )
        dataset.append_col([financial_year] * dataset.height, header="Financial Year")

    def __init__(self, request=None, *args, **kwargs):
        super(ProvInfraProjectSnapshotResource, self).__init__()
        self.request = request


class IRMReportSheet(object):
    def __init__(self, data_set):
        self.data_set = data_set
        self.data_set_dict = data_set.dict
        self.output_data_set = self.create_output_data_set()
        self.contractor_columns = self._get_project_contractor_columns(data_set)
        self.row_to_delete = []

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
        self.delete_empty_rows()

    def process_row(self, row_index):
        row = self.data_set[row_index]
        if is_empty_row(row):
            self.row_to_delete.append(row_index)
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

    def delete_empty_rows(self):
        for index in reversed(self.row_to_delete):
            del self.data_set[index]


def is_empty_cell(cell):
    return not cell or (isinstance(cell, basestring) and len(cell.strip()) == 0)


def is_not_empty_cell(cell):
    return not is_empty_cell(cell)


def is_empty_row(row):
    return len(list(filter(is_not_empty_cell, row))) == 0
