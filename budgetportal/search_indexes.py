from haystack import indexes
from budgetportal.models import ProvInfraProject


class ProvInfraProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    province = indexes.CharField(use_template=True)

    def get_model(self):
        return ProvInfraProject
