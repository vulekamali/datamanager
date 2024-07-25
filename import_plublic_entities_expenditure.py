import csv
from budgetportal.models import (
    FinancialYear,
    Sphere,
    Government,
    Department,
)

from budgetportal.models.government import PublicEntity, PublicEntityExpenditure


def make_financial_year(year):
    # Check if the input is a valid year
    try:
        year = int(year)
    except ValueError:
        return "Invalid year format"

    financial_year_str = f"{year - 1}-{str(year)[2:]}"

    return financial_year_str


# Open the CSV file
with open("ENT_ENE_CashFlow_202324 - Data.csv", newline="") as csvfile: 
    # Create a DictReader object with named columns
    csvreader = csv.DictReader(csvfile)

    foundGovernments = []
    notFoundFinancialYears = []
    notFoundGovernments = []
    notFoundDepartments = []
    notFoundSpheres = []
    alreadyFoundDepartments = []
    notFoundPublicEntities = []

    count = 0
    # Loop through each row in the CSV file
    for row in csvreader:
        if count >= 10:
            break

        # Increment the counter
        count += 1
        # Access each column by its name
        vote = row["Vote"]
        department = row["Department"]
        entity_name = row["EntityName"]
        consol_indi = row["ConsolIndi"]
        pfma = row["PFMA"]
        type_ = row["Type"]
        economic_classification1 = row["EconomicClassification1"]
        economic_classification2 = row["EconomicClassification2"]
        economic_classification3 = row["EconomicClassification3"]
        economic_classification4 = row["EconomicClassification4"]
        economic_classification5 = row["EconomicClassification5"]
        economic_classification6 = row["EconomicClassification6"]
        function_group1 = row["FunctionGroup1"]
        function_group2 = row["FunctionGroup2"]
        financial_year = row["FinancialYear"]
        budget_phase = row["BudgetPhase"]
        amount_r_thou = row["Amount (R-Thou)"]
        amount = row["Amount"]

        financial_year_slug = make_financial_year(financial_year)
        financialYears = FinancialYear.objects.filter(slug=financial_year_slug)

        if financialYears:
            selectedFinancialYear = financialYears.first()
            spheres = Sphere.objects.filter(
                slug="national", financial_year=selectedFinancialYear
            )

            if spheres:
                selectedSphere = spheres.first()
                governments = Government.objects.filter(sphere=selectedSphere)

                if governments:
                    selectedGovernment = governments.first()
                    foundGovernments.append(selectedGovernment)

                    departments = Department.objects.filter(
                        name=department, government=selectedGovernment
                    )
                    selectedDepartment = None

                    if departments:
                        selectedDepartment = departments.first()
                    else:
                        notFoundDepartments.append(
                            f"Department {department} for financial year {financial_year_slug} does not exist"
                        )
                        try:
                            selectedDepartment = Department.objects.create(
                                name=department,
                                government=selectedGovernment,
                                vote_number=vote,
                            )
                        except:
                            alreadyFoundDepartments.append(
                                f"Department {department} for financial year {financial_year_slug} already exists"
                            )
                    if selectedDepartment:
                        publicEntities = PublicEntity.objects.filter(
                            name=entity_name,
                            department=selectedDepartment,
                            government=selectedGovernment,
                            pfma=pfma,
                            functiongroup1=function_group1,
                        )
                        selectedPublicEntity = None

                        if publicEntities:
                            selectedPublicEntity = publicEntities.first()
                        else:
                            selectedPublicEntity = PublicEntity.objects.create(
                                name=entity_name,
                                department=selectedDepartment,
                                government=selectedGovernment,
                                pfma=pfma,
                                functiongroup1=function_group1,
                            )

                        if selectedPublicEntity:
                            selectedPublicEntityExpenditure = (
                                PublicEntityExpenditure.objects.create(
                                    public_entity=selectedPublicEntity,
                                    amount=amount,
                                    budget_phase=budget_phase,
                                    expenditure_type=type_,
                                    economic_classification1=economic_classification1,
                                    economic_classification2=economic_classification2,
                                    economic_classification3=economic_classification3,
                                    economic_classification4=economic_classification4,
                                    economic_classification5=economic_classification5,
                                    economic_classification6=economic_classification6,
                                    consol_indi=consol_indi,
                                )
                            )

                        else:
                            notFoundPublicEntities.append(
                                f"Public entity {entity_name} for department {department} for financial year {financial_year_slug} does not exist/not created"
                            )

                else:
                    notFoundGovernments.append(
                        f"Government for financial year {financial_year_slug} does not exist"
                    )
            else:
                notFoundSpheres.append(
                    f"National sphere for financial year {financial_year_slug} does not exist"
                )
        else:
            notFoundFinancialYears.append(
                f"Financial year {financial_year_slug} does not exist"
            )

    print("-------------------------------------")
    print(foundGovernments)
    print("-------------------------------------")
    print(notFoundFinancialYears)
    print("-------------------------------------")
    print(notFoundSpheres)
    print("-------------------------------------")
    print(notFoundGovernments)
    print("-------------------------------------")
    print(notFoundDepartments)
    print("-------------------------------------")
    print(alreadyFoundDepartments)
    print("-------------------------------------")
    print(notFoundPublicEntities)


# Add up publicExpenditure for each publicEntity
for publicEntity in PublicEntity.objects.all():
    totalExpenditure = 0
    for publicEntityExpenditure in PublicEntityExpenditure.objects.filter(
        public_entity=publicEntity
    ):
        totalExpenditure += publicEntityExpenditure.amount
    publicEntity.amount = totalExpenditure
    publicEntity.save()
    print(
        f"Public entity {publicEntity.name} has total expenditure of {publicEntity.amount}"
    )
