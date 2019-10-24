from django.apps import AppConfig

class BudgetPortalConfig(AppConfig):
    name = 'budgetportal'
    verbose_name = "Budget Portal"

    def ready(self):
        import budgetportal.signals #noqa
