from haystack import indexes
from budgetportal.models import ProvInfraProject


class ProvInfraProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(use_template=True)
    province = indexes.CharField(use_template=True, faceted=True)
    department = indexes.CharField(use_template=True, faceted=True)
    status = indexes.CharField(use_template=True, faceted=True)
    primary_funding_source = indexes.CharField(use_template=True, faceted=True)
    estimated_completion_date = indexes.DateField(use_template=True)
    total_project_cost = indexes.FloatField(use_template=True)

    def get_model(self):
        return ProvInfraProject
