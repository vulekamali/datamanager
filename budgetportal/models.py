from django.db import models


class FinancialYear(models.Model):
    organisational_unit = 'financial_year'

    slug = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return self.slug
