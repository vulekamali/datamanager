def order_chart_data(snapshot_list):
    return sorted(snapshot_list, key=lambda x: x["date"])


def time_series_data(project_snapshots):
    """This function expects a list of InfraProjectSnapshots of the same
    project,in IRMSnapshot order."""
    chart_data = {"snapshots": [], "events": []}
    for snapshot in project_snapshots:
        quarter_number = snapshot.irm_snapshot.quarter.number
        fin_year = snapshot.irm_snapshot.financial_year

        total_estimated_project_cost = snapshot.estimated_total_project_cost
        status = snapshot.status
        date, quarter_label, fin_year_label = extract_date_quarter_year(
            quarter_number, fin_year
        )
        total_spent_to_date, total_spent_in_quarter = compute_total_spent(
            snapshot, quarter_number
        )
        chart_data["snapshots"].append(
            {
                "date": date,
                "quarter_label": quarter_label,
                "financial_year_label": fin_year_label,
                "total_spent_to_date": total_spent_to_date,
                "total_spent_in_quarter": total_spent_in_quarter,
                "total_estimated_project_cost": total_estimated_project_cost,
                "status": status,
            }
        )
        if quarter_number > 1:
            chart_data = update_previous_chart_values(
                chart_data, snapshot, quarter_number, fin_year
            )
    chart_data["snapshots"] = order_chart_data(chart_data["snapshots"])

    latest_snapshot = project_snapshots[-1]
    chart_data["events"] = extract_events(latest_snapshot)

    return chart_data


def update_previous_chart_values(chart_data, snapshot, quarter_number, fin_year):
    for i in range(quarter_number, 0, -1):
        quarter_is_found = False
        date, quarter_label, fin_year_label = extract_date_quarter_year(i, fin_year)
        total_spent_to_date, total_spent_in_quarter = compute_total_spent(snapshot, i)
        for data in chart_data["snapshots"]:
            if data["date"] == date:
                data.update(
                    {
                        "total_spent_to_date": total_spent_to_date,
                        "total_spent_in_quarter": total_spent_in_quarter,
                    }
                )
                quarter_is_found = True

        if quarter_is_found is False:
            chart_data["snapshots"].append(
                {
                    "date": date,
                    "quarter_label": quarter_label,
                    "financial_year_label": fin_year_label,
                    "total_spent_to_date": total_spent_to_date,
                    "total_spent_in_quarter": total_spent_in_quarter,
                    "total_estimated_project_cost": None,
                    "status": None,
                }
            )
    return chart_data


def extract_date_quarter_year(quarter_number, financial_year):
    dates = {1: "-06-30", 2: "-09-30", 3: "-12-31", 4: "-03-31"}
    if quarter_number == 4:
        date = str(int(financial_year.get_starting_year()) + 1) + dates[quarter_number]
    else:
        date = financial_year.get_starting_year() + dates[quarter_number]

    quarter_label = "END Q{}".format(quarter_number)
    financial_year_label = ""
    if quarter_number == 1:
        financial_year_label = financial_year.slug

    return date, quarter_label, financial_year_label


def compute_total_spent(project_snapshot, quarter_number):
    total_spent_in_quarter = None
    total_spent_to_date = None
    total_from_previous_years = project_snapshot.expenditure_from_previous_years_total
    if total_from_previous_years is not None:
        total_spent_to_date = total_from_previous_years

    for i in range(1, quarter_number + 1):
        field = "actual_expenditure_q{}".format(i)
        quarterly_spent = getattr(project_snapshot, field)
        if quarterly_spent is None:
            total_spent_to_date = None

        if total_spent_to_date:
            total_spent_to_date += quarterly_spent

        if i == quarter_number:
            total_spent_in_quarter = quarterly_spent

    return total_spent_to_date, total_spent_in_quarter


def extract_events(project_snapshot):
    events = []
    start_date = project_snapshot.start_date
    if start_date:
        events.append({"date": str(start_date), "label": "Project Start Date"})

    estimated_const_start_date = project_snapshot.estimated_construction_start_date
    if estimated_const_start_date:
        events.append(
            {
                "date": str(estimated_const_start_date),
                "label": "Estimated Construction Start Date",
            }
        )
    estimated_completion_date = project_snapshot.estimated_completion_date
    if estimated_completion_date:
        events.append(
            {
                "date": str(estimated_completion_date),
                "label": "Estimated Completion Date",
            }
        )
    contracted_construction_end_date = project_snapshot.contracted_construction_end_date
    if contracted_construction_end_date:
        events.append(
            {
                "date": str(contracted_construction_end_date),
                "label": "Contracted Construction End Date",
            }
        )

    estimated_construction_end_date = project_snapshot.estimated_construction_end_date
    if estimated_construction_end_date:
        events.append(
            {
                "date": str(estimated_construction_end_date),
                "label": "Estimated Construction End Date",
            }
        )

    return events
