from import_export.instance_loaders import BaseInstanceLoader
from import_export import resources
from budgetportal.models import (
    Department,
    Government,
    Sphere,
)

from import_export.fields import Field
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from import_export.widgets import Widget

class CustomIsVotePrimaryWidget(Widget):
    """
    Widget for converting is_vote_primary fields.
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
    """
    Widget for converting government_name and sphere fields to governments.
    """

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


class DepartmentResource(resources.ModelResource):
    is_vote_primary = Field(attribute='is_vote_primary', column_name='is_vote_primary', widget=CustomIsVotePrimaryWidget())
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
