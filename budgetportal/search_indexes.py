from haystack import indexes
from budgetportal.models import ProvInfraProject, ProvInfraProjectSnapshot
from django.db.models import Prefetch, OuterRef, Subquery, Max


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
        return object.project_snapshots.latest().estimated_completion_date.isoformat()

    def prepare_latitude(sef, object):
        return object.project_snapshots.latest().latitude

    def prepare_longitude(sef, object):
        return object.project_snapshots.latest().longitude

    def prepare_url_path(sef, object):
        return object.get_absolute_url()

    def should_update(self, instance, **kwargs):
        return instance.project_snapshots.count()

    # def index_queryset(self, using=None):
    #     "Used when the entire index for model is updated."
    #     return (
    #         self.get_model()
    #         .objects.all()
    #         .prefetch_related(
    #             "project_snapshots",
    #             "project_snapshots__irm_snapshot",
    #             "project_snapshots__irm_snapshot__financial_year",
    #             "project_snapshots__irm_snapshot__quarter",
    #         )
    #     )
    # hottest_cakes = Cake.objects.filter(
    #    baked_at=Subquery(
    #        (Cake.objects
    #            .filter(bakery=OuterRef('bakery'))
    #            .values('bakery')
    #            .annotate(last_bake=Max('baked_at'))
    #            .values('last_bake')[:1]
    #        )
    #    )
    # )
    # bakeries = Bakery.objects.all().prefetch_related(
    #     Prefetch('cake_set',
    #         queryset=hottest_cakes,
    #         to_attr='hottest_cakes'
    #     )
    # )
    # for bakery in bakeries:
    #    print 'Bakery %s has %s hottest_cakes' % (bakery, len(bakery.hottest_cakes))
    # -----------------------
    # latest_snapshots = ProvInfraProjectSnapshot.objects.filter(
    #     project=Subquery(
    #         (
    #             ProvInfraProjectSnapshot.objects.filter(
    #                 project=OuterRef("project"), status="Tender"
    #             )
    #             .values("project")
    #             .annotate(latest_snapshot=Max("project"))
    #             .values("latest_snapshot")[:1]
    #         )
    #     )
    # )
    #
    # return self.get_model().objects.all().prefetch_related(
    #     Prefetch(
    #         "project_snapshots", queryset=latest_snapshots, to_attr="latest_snapshots"
    #     )
    # )
    # ===================
