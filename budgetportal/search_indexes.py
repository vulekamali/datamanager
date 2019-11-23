from haystack import indexes
from budgetportal.models import ProvInfraProject, ProvInfraProjectSnapshot
from django.db.models import Prefetch, OuterRef, Subquery, Max, Count


class ProvInfraProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField()
    province = indexes.CharField(faceted=True)
    department = indexes.CharField(faceted=True)
    status = indexes.CharField(faceted=True)
    primary_funding_source = indexes.CharField(faceted=True)
    estimated_completion_date = indexes.DateField()
    total_project_cost = indexes.FloatField()
    latitude = indexes.CharField()
    longitude = indexes.CharField()
    url_path = indexes.CharField()

    def get_model(self):
        return ProvInfraProject

    def prepare_name(sef, object):
        return object.project_snapshots.latest().name

    def prepare_status(sef, object):
        return object.project_snapshots.latest().status

    def prepare_province(sef, object):
        return object.project_snapshots.latest().province

    def prepare_department(sef, object):
        return object.project_snapshots.latest().department

    def prepare_primary_funding_source(sef, object):
        return object.project_snapshots.latest().primary_funding_source

    def prepare_total_project_cost(sef, object):
        return object.project_snapshots.latest().total_project_cost

    def prepare_estimated_completion_date(sef, object):
        date = object.project_snapshots.latest().estimated_completion_date
        if date:
            return date.isoformat()

    def prepare_latitude(sef, object):
        return object.project_snapshots.latest().latitude

    def prepare_longitude(sef, object):
        return object.project_snapshots.latest().longitude

    def prepare_url_path(sef, object):
        return object.get_absolute_url()

    def should_update(self, instance, **kwargs):
        return instance.project_snapshots.count()

    def index_queryset(self, using=None):
        return ProvInfraProject.objects.annotate(
            project_snapshots_count=Count("project_snapshots")
        ).filter(project_snapshots_count__gte=1)
