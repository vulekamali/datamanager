from django.contrib import admin
from budgetportal.models import FinancialYear


class FinancialYearAdmin(admin.ModelAdmin):
    pass


admin.site.register(FinancialYear, FinancialYearAdmin)
