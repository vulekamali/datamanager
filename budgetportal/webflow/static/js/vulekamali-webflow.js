(function() {
    if ($("body.provincial-infrastructure-project-detail-page")) {
        $(".project-name-field").html(pageData.project.name);
        $(".total-project-cost-field").html(pageData.project.total_project_cost);
        $(".province-name-field").html(pageData.project.province);
        $(".department-name-field").html(pageData.project.department);
    }

})();
