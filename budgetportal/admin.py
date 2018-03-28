from django.contrib import admin
from django.views.generic import TemplateView

from budgetportal.models import (
    Department,
    FinancialYear,
    Government,
    GovtFunction,
    Programme,
    Sphere,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


admin.site.login = login_required(admin.site.login)

class FinancialYearAdmin(admin.ModelAdmin):
    pass


class SphereAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class GovernmentAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class GovtFunctionAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'vote_number',
        'name',
        'get_government',
        'get_sphere',
        'get_financial_year',
    )
    list_display_links = (
        'vote_number',
        'name',
    )
    list_filter = (
        'government__sphere__financial_year__slug',
        'government__sphere__name',
        'government__name',
    )
    search_fields = (
        'government__sphere__financial_year__slug',
        'government__sphere__name',
        'government__name',
        'name',
    )
    readonly_fields = ('slug',)
    list_per_page = 20

    def get_government(self, obj):
        return obj.government.name

    def get_sphere(self, obj):
        return obj.government.sphere.name

    def get_financial_year(self, obj):
        return obj.government.sphere.financial_year.slug


class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        'programme_number',
        'name',
        'get_department',
        'get_government',
        'get_sphere',
        'get_financial_year',
    )
    list_display_links = (
        'programme_number',
        'name',
    )
    list_filter = (
        'department__government__sphere__financial_year__slug',
        'department__government__sphere__name',
        'department__government__name',
        'department__name',
    )
    search_fields = (
        'department__government__sphere__financial_year__slug',
        'department__government__sphere__name',
        'department__government__name',
        'department__name',
        'name',
    )
    readonly_fields = ('slug',)

    def get_department(self, obj):
        return obj.department.name

    def get_government(self, obj):
        return obj.department.government.name

    def get_sphere(self, obj):
        return obj.department.government.sphere.name

    def get_financial_year(self, obj):
        return obj.department.government.sphere.financial_year.slug


class EntityDatasetsView(TemplateView):
    template_name = "admin/entity_datasets.html"
    financial_year_slug = None
    sphere_slug = None

    def get_context_data(self, **kwargs):
        sphere = Sphere.objects.get(
            financial_year__slug=self.financial_year_slug,
            slug=self.sphere_slug,
        )
        return {
            'sphere': sphere,
        }


class UserAdmin(admin.ModelAdmin):
    pass


class SiteAdmin(admin.ModelAdmin):
    pass


for financial_year in FinancialYear.objects.all():
    for sphere in financial_year.spheres.all():
        view = EntityDatasetsView.as_view(
            financial_year_slug=financial_year.slug,
            sphere_slug=sphere.slug,
        )
        path = "%s/%s/entity_datasets" % (financial_year.slug, sphere.slug)
        label = "Entity Datasets - %s %s" % (financial_year.slug, sphere.name)
        admin.site.register_view(path, label, view=view)

admin.site.register(FinancialYear, FinancialYearAdmin)
admin.site.register(Sphere, SphereAdmin)
admin.site.register(Government, GovernmentAdmin)
admin.site.register(GovtFunction, GovtFunctionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Site, SiteAdmin)
