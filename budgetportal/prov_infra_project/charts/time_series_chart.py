import simplejson as json


def time_series_data(project):
    chart_data = {"snapshots": [], "events": []}
    project_snapshots = project.project_snapshots.all()
    for snapshot in project_snapshots:
        quarter = snapshot.irm_snapshot.quarter
        fin_year = snapshot.irm_snapshot.financial_year

        total_estimated_project_cost = snapshot.total_project_cost
        status = snapshot.status
        date, quarter_label, fin_year_label = extract_date_quarter_year(
            quarter.number, fin_year
        )
        total_spent_to_date, total_spent_in_quarter = compute_total_spent(
            snapshot, quarter.number
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
        if quarter.number > 1:
            chart_data = update_previous_chart_values(
                chart_data, snapshot, quarter, fin_year
            )

    latest_snapshot = project.project_snapshots.latest()
    chart_data["events"] = extract_events(latest_snapshot)
    return json.dumps(chart_data, use_decimal=True)


def update_previous_chart_values(chart_data, snapshot, quarter, fin_year):
    for i in range(quarter.number, 0, -1):
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
    return chart_data


def extract_date_quarter_year(quarter_number, financial_year):
    dates = {1: "-06-30", 2: "-09-30", 3: "-12-31", 4: "-03-31"}
    date = financial_year.get_starting_year() + dates[quarter_number]
    quarter_label = "END Q{}".format(quarter_number)
    financial_year_label = ""
    if quarter_number == 1:
        financial_year_label = financial_year.slug

    return date, quarter_label, financial_year_label


def compute_total_spent(project_snapshot, quarter_number):
    total_spent_to_date = project_snapshot.expenditure_from_previous_years_total
    total_spent_in_quarter = None

    for i in range(1, quarter_number + 1):
        field = "actual_expenditure_q{}".format(i)
        quarterly_spent = getattr(project_snapshot, field)
        if quarterly_spent is None:
            total_spent_in_quarter = None
            total_spent_to_date = None
            break

        total_spent_to_date += quarterly_spent

        if i == quarter_number:
            total_spent_in_quarter = quarterly_spent

    return total_spent_to_date, total_spent_in_quarter


def extract_events(project_snapshot):
    events = []
    start_date = project_snapshot.estimated_construction_start_date
    events.append(
        {"date": str(start_date), "label": "Estimated construction start date"}
    )
    end_date = project_snapshot.estimated_construction_end_date
    events.append({"date": str(end_date), "label": "Estimated construction end date"})

    return events
