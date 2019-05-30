from budgetportal.models import Department, Government, Sphere
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from import_export import resources
from import_export.admin import ImportForm
from import_export.fields import Field
from import_export.formats import base_formats
from import_export.instance_loaders import ModelInstanceLoader
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
            raise ValidationError(
                "Government '%s' does not exist in sphere '%s'." %
                (value, self.sphere))

        return government


class DepartmentInstanceLoader(ModelInstanceLoader):
    """
    Class to find a Department model instance from a row.
    """

    def get_instance(self, row):
        """
        Gets a Department instance by either a unique government-slug or
        government-name combination, or if is_vote_primary is True, from a
        unique government-vote_number combination.
        """
        name = self.resource.fields['name'].clean(row)
        slug = slugify(name)
        government = self.resource.fields['government'].clean(row)

        instance = None

        try:
            instance = Department.objects.get(name=name, government=government)
        except Department.DoesNotExist:
            pass

        if not instance:
            try:
                instance = Department.objects.get(slug=slug, government=government)
            except Department.DoesNotExist:
                pass

        # If is_vote_primary, then (government, vote_number) must be unique
        is_vote_primary = self.resource.fields['is_vote_primary'].clean(row)
        vote_number = self.resource.fields['vote_number'].clean(row)
        if is_vote_primary:
            try:
                instance = Department.objects.get(
                    vote_number=vote_number, government=government)
            except Department.DoesNotExist:
                pass

        if instance:
            return instance

        return None


class DepartmentResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in department
    import files to django models.
    """
    is_vote_primary = Field(attribute='is_vote_primary',
                            column_name='is_vote_primary', widget=CustomIsVotePrimaryWidget())
    name = Field(attribute='name', column_name='department_name')
    vote_number = Field(attribute='vote_number', column_name='vote_number')
    government = Field(attribute='government',
                       column_name='government', widget=CustomGovernmentWidget())

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


class DepartmentImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import departments.
    """
    sphere = forms.ModelChoiceField(
        queryset=Sphere.objects.all(),
        required=True
    )
