from django.contrib import admin
from django.views.generic import TemplateView
from import_export.formats import base_formats
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportForm, ImportMixin, ConfirmImportForm
from django.core.exceptions import ValidationError
from import_export.widgets import Widget
from import_export.instance_loaders import BaseInstanceLoader
from import_export.fields import Field
from django import forms
from django.utils.text import slugify

from budgetportal.models import (
    Department,
    FinancialYear,
    Government,
    GovtFunction,
    Programme,
    Sphere,
)
from budgetportal.bulk_upload import bulk_upload_view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.utils import ProgrammingError
from django.contrib import messages
import logging


logger = logging.getLogger(__name__)
admin.site.login = login_required(admin.site.login)


class FinancialYearAdmin(admin.ModelAdmin):
    pass


class SphereAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class GovernmentAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class GovtFunctionAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


class DepartmentInstanceLoader(BaseInstanceLoader):

    def get_queryset(self):
        return self.resource._meta.model.objects.all()

    def get_instance(self, row):
        unique_together = (
            ('government', 'slug'),
            ('government', 'name'),
        )
        for fields in unique_together:
            params = {}
            for key in fields:
                if key == 'slug':
                    field = self.resource.fields['name']
                    params['slug'] = slugify(field.clean(row))
                else:
                    field = self.resource.fields[key]
                    params[field.attribute] = field.clean(row)
            if params:
                try:
                    instance = self.get_queryset().get(**params)
                    if instance:
                        return instance
                except self.resource._meta.model.DoesNotExist:
                    pass

        try:
            params = {}
            # If is_vote_primary, then (government, vote_number) must be unique
            is_vote_primary_field = self.resource.fields['is_vote_primary']
            is_vote_primary = is_vote_primary_field.clean(row)
            if is_vote_primary:
                import_id_fields = ['government', 'vote_number']
                for key in import_id_fields:
                    field = self.resource.fields[key]
                    params[field.attribute] = field.clean(row)
                if params:
                    instance = self.get_queryset().get(**params)
                    if instance:
                        return instance

            return None
        except self.resource._meta.model.DoesNotExist:
            return None



class CustomBooleanWidget(Widget):
    """
    Widget for converting boolean fields.
    """

    def render(self, value, obj=None):
        if value:
            return "True"
        else:
            return "False"

    def clean(self, value, row=None, *args, **kwargs):
        if value is None or value == "" or value.upper() == 'TRUE':
            return True
        else:
            return False

class CustomGovernmentWidget(Widget):
    def set_sphere(self, sphere):
        try:
            self.sphere = Sphere.objects.get(id=sphere)
        except Sphere.DoesNotExist:
            raise ValidationError('Sphere with id %s does not exist.' % sphere)

    def render(self, value, obj=None):
        return value.name

    def clean(self, value, row=None, *args, **kwargs):
        try:
            government = Government.objects.get(
                sphere=self.sphere,
                slug=slugify(value),
            )
        except Government.DoesNotExist:
            raise ValidationError("Government '%s' with sphere '%s' does not exist." % (value, self.sphere))

        return government

class DepartmentResource(resources.ModelResource):
    is_vote_primary = Field(attribute='is_vote_primary', column_name='is_vote_primary', widget=CustomBooleanWidget())
    name = Field(attribute='name', column_name='department_name')
    government = Field(attribute='government', column_name='government', widget=CustomGovernmentWidget())

    class Meta:
        model = Department
        fields = ('government', 'name', 'vote_number',
        'is_vote_primary', 'intro', 'website_url')
        instance_loader_class = DepartmentInstanceLoader
        import_id_fields = ['government', 'name']

    def __init__(self, *args, **kwargs):
        if 'sphere' in kwargs:
            self.sphere = kwargs['sphere']
            self.fields['government'].widget.set_sphere(self.sphere)

class CustomImportForm(ImportForm):
    sphere = forms.ModelChoiceField(
        queryset=Sphere.objects.all(),
        required=True
    )

class CustomConfirmImportForm(ConfirmImportForm):
    sphere = forms.ModelChoiceField(
        queryset=Sphere.objects.all(),
        required=True
    )


class DepartmentAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = DepartmentResource
    formats = ( base_formats.CSV, )

    def get_import_form(self):
        return CustomImportForm

    def get_confirm_import_form(self):
        return CustomConfirmImportForm

    def get_resource_kwargs(self, request, *args, **kwargs):
        if hasattr(self, 'sphere'):
            return {'sphere': self.sphere}
        if u'sphere' in request.POST:
            print('sphere ', request.POST[u'sphere'])
            self.sphere = request.POST[u'sphere']
            return {'sphere': request.POST[u'sphere']}
        return {}

    def get_form_kwargs(self, form, *args, **kwargs):
        # pass on `sphere` to the kwargs for the custom confirm form
        if isinstance(form, CustomImportForm):
            if form.is_valid():
                sphere = form.cleaned_data['sphere']
                kwargs.update({'sphere': sphere.id})
        return kwargs

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


# admin.site.register_view('bulk_upload', 'Bulk Upload', view=bulk_upload_view)


# try:
#     for financial_year in FinancialYear.objects.all():
#         for sphere in financial_year.spheres.all():
#             view = EntityDatasetsView.as_view(
#                 financial_year_slug=financial_year.slug,
#                 sphere_slug=sphere.slug,
#             )
#             path = "%s/%s/entity_datasets" % (financial_year.slug, sphere.slug)
#             label = "Entity Datasets - %s %s" % (financial_year.slug, sphere.name)
#             admin.site.register_view(path, label, view=view)
# except ProgrammingError, e:
#     logging.error(e, exc_info=True)


admin.site.register(FinancialYear, FinancialYearAdmin)
admin.site.register(Sphere, SphereAdmin)
admin.site.register(Government, GovernmentAdmin)
admin.site.register(GovtFunction, GovtFunctionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Site, SiteAdmin)
