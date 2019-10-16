(function() {

    function formatCurrency(decimalString) {
        if (decimalString == null)
            return "";
        return "R " + Math.round(parseFloat(decimalString)).toLocaleString();
    }

    if ($("body.provincial-infrastructure-project-detail-page")) {
        // Project definition
        $(".name-field").html(pageData.project.name);
        $(".project-number-field").html(pageData.project.project_number);
        $(".budget-programme-field").html(pageData.project.budget_programme);
        $(".nature-of-investment-field").html(pageData.project.nature_of_investment);

        // Administrative details
        $(".primary-funding-source-field").html(pageData.project.primary_funding_source);
        $(".funding-status-field").html(pageData.project.funding_status);
        $(".province-field").html(pageData.project.province);
        $(".department-field").html(pageData.project.department);

        // Location
        $(".local-municipality-field").html(pageData.project.local_municipality);
        $(".district-municipality-field").html(pageData.project.district_municipality);
        $(".coordinates-field").html(pageData.project.latitude + ", " + pageData.project.longitude);

        // Implementation
        $(".program-implementing-agent-field").html(pageData.project.program_implementing_agent);
        $(".principle-agent-field").html(pageData.project.principle_agent);
        $(".main-contractor-field").html(pageData.project.main_contractor);
        $(".other-service-providers-field").html(pageData.project.other_parties);

        // Dates
        $(".status-field").html(pageData.project.status);
        $(".start-date-field").html(pageData.project.start_date);
        $(".estimated-construction-start-date-field").html(pageData.project.estimated_construction_start_date);
        $(".estimated-completion-date-field").html(pageData.project.estimated_completion_date);
        $(".contracted-construction-end-date-field").html(pageData.project.contracted_construction_end_date);
        $(".estimated-construction-end-date-field").html(pageData.project.estimated_construction_end_date);

        // Budgets and spending
        $(".total-project-cost-field").html(formatCurrency(pageData.project.total_project_cost));
        $(".total-professional-fees-field").html(formatCurrency(pageData.project.total_professional_fees));
        $(".total-construction-costs-field").html(formatCurrency(pageData.project.total_construction_costs));
        $(".variation-orders-field").html(formatCurrency(pageData.project.variation_orders));
        $(".expenditure-from-previous-years-professional-fees-field").html(formatCurrency(pageData.project.expenditure_from_previous_years_professional_fees));
        $(".expenditure-from-previous-years-construction-costs-field").html(formatCurrency(pageData.project.expenditure_from_previous_years_construction_costs));
        $(".expenditure-from-previous-years-total-field").html(formatCurrency(pageData.project.expenditure_from_previous_years_total));
        $(".project-expenditure-total-field").html(formatCurrency(pageData.project.project_expenditure_total));
        $(".main-appropriation-professional-fees-field").html(formatCurrency(pageData.project.main_appropriation_professional_fees));
        $(".adjustment-appropriation-professional-fees-field").html(formatCurrency(pageData.project.adjustment_appropriation_professional_fees));
        $(".main-appropriation-construction-costs-field").html(formatCurrency(pageData.project.main_appropriation_construction_costs));
        $(".adjustment-appropriation-construction-costs-field").html(formatCurrency(pageData.project.adjustment_appropriation_construction_costs));
        $(".main-appropriation-total-field").html(formatCurrency(pageData.project.main_appropriation_total));
        $(".adjustment-appropriation-total-field").html(formatCurrency(pageData.project.adjustment_appropriation_total));
        $(".actual-expenditure-q1-field").html(formatCurrency(pageData.project.actual_expenditure_q1));
        $(".actual-expenditure-q2-field").html(formatCurrency(pageData.project.actual_expenditure_q2));
        $(".actual-expenditure-q3-field").html(formatCurrency(pageData.project.actual_expenditure_q3));
        $(".actual-expenditure-q4-field").html(formatCurrency(pageData.project.actual_expenditure_q4));

        // Maps and visualisations
        $(".embed-container").css("background-color", "#e1e1e1");

    }

})();
