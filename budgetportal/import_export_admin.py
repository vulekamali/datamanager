import logging

from budgetportal import models
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import NOT_PROVIDED, Q
from django.utils.text import slugify
from import_export import resources
from import_export.admin import ImportForm
from import_export.fields import Field
from import_export.instance_loaders import ModelInstanceLoader
from import_export.widgets import Widget

logger = logging.getLogger(__name__)


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
        if isinstance(value, bool):
            return value
        elif (
            value is None
            or value == ""
            or value.upper() == "TRUE"
            or value.upper() == "=TRUE()"
        ):
            return True
        else:
            return False


class CustomProvinceWidget(Widget):
    """
    Helper class for converting gps_code fields on the InfrastructureProjectPart model.
    """

    def clean(self, value, row=None, *args, **kwargs):
        project_name = row["project_name"]
        gps_code = row["gps_code"]
        cleaned_coordinates = models.InfrastructureProjectPart.clean_coordinates(
            gps_code
        )
        provinces = models.InfrastructureProjectPart.get_provinces(
            cleaned_coordinates=cleaned_coordinates, project_name=project_name
        )
        value = "".join([province for province in provinces])
        return value


class CustomGovernmentWidget(Widget):
    """
    Widget for converting government_name and sphere fields to governments.
    """

    def set_sphere(self, sphere):
        try:
            self.sphere = models.Sphere.objects.get(id=sphere)
        except models.Sphere.DoesNotExist:
            raise ValidationError("Sphere with id %s does not exist." % sphere)

    def render(self, value, obj=None):
        return value.name

    def clean(self, value, row=None, *args, **kwargs):
        try:
            government = models.Government.objects.get(
                sphere=self.sphere, slug=slugify(value)
            )
        except models.Government.DoesNotExist:
            raise ValidationError(
                "Government '%s' does not exist in sphere '%s'." % (value, self.sphere)
            )

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
        name = self.resource.fields["name"].clean(row)
        slug = slugify(name)
        government = self.resource.fields["government"].clean(row)

        q = Q(name=name, government=government)
        q |= Q(slug=slug, government=government)

        # If is_vote_primary, then (government, vote_number) must be unique
        is_vote_primary = self.resource.fields["is_vote_primary"].clean(row)
        vote_number = self.resource.fields["vote_number"].clean(row)

        if is_vote_primary:
            q |= Q(vote_number=vote_number, government=government)

        try:
            return models.Department.objects.get(q)
        except models.Department.DoesNotExist:
            pass

        return None

class PublicEntityInstanceLoader(ModelInstanceLoader):
    """
    Class to find a Public Entity model instance from a row.
    """

    def get_instance(self, row):
        """
        Gets a Public Entity instance by either a unique government-slug or
        government-name combination.
        """
        name = self.resource.fields["name"].clean(row)
        slug = slugify(name)
        government = self.resource.fields["government"].clean(row)

        q = Q(name=name, government=government)
        q |= Q(slug=slug, government=government)

        try:
            return models.PublicEntity.objects.get(q)
        except models.PublicEntity.DoesNotExist:
            pass

        return None


class DepartmentResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in department
    import files to django models.
    """

    is_vote_primary = Field(
        attribute="is_vote_primary",
        column_name="is_vote_primary",
        widget=CustomBooleanWidget(),
    )
    name = Field(attribute="name", column_name="department_name")
    vote_number = Field(attribute="vote_number", column_name="vote_number")
    government = Field(
        attribute="government",
        column_name="government",
        widget=CustomGovernmentWidget(),
    )

    class Meta:
        model = models.Department
        fields = (
            "government",
            "name",
            "vote_number",
            "is_vote_primary",
            "intro",
            "website_url",
        )
        instance_loader_class = DepartmentInstanceLoader
        import_id_fields = ["government", "name"]

    def __init__(self, *args, **kwargs):
        if "sphere" in kwargs:
            self.sphere = kwargs["sphere"]
            self.fields["government"].widget.set_sphere(self.sphere)


class PublicEntityResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in public entity
    import files to django models.
    """

    name = Field(attribute="name", column_name="entity_name")
    pfma = Field(attribute="pfma", column_name="pfma")
    functiongroup1 = Field(attribute="functiongroup1", column_name="functiongroup1")
    government = Field(
        attribute="government",
        column_name="government",
        widget=CustomGovernmentWidget(),
    )

    class Meta:
        model = models.PublicEntity
        fields = (
            "government",
            "name",
            "pfma",
            "functiongroup1"
            )
        instance_loader_class = PublicEntityInstanceLoader
        import_id_fields = ["government", "name"]

    def __init__(self, *args, **kwargs):
        if "sphere" in kwargs:
            self.sphere = kwargs["sphere"]
            self.fields["government"].widget.set_sphere(self.sphere)


class DepartmentImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import departments.
    """

    sphere = forms.ModelChoiceField(queryset=models.Sphere.objects.all(), required=True)


class PublicEntityImportForm(ImportForm):
    """
    Form class to use to upload a CSV file to import public entities.
    """

    sphere = forms.ModelChoiceField(queryset=models.Sphere.objects.all(), required=True)



class InfrastructureProjectProvinceField(Field):
    """
    The only reason to override this class is so that we can force the clean()
    method to run on the provinces field, even though it doesn't exist in the
    import csv. The reason for this being that it doesn't seem like there's
    another easy way to 'create' a new field by using other fields.
    """

    def clean(self, data):
        """
        Translates the value stored in the imported datasource to an
        appropriate Python object and returns it.
        """
        if self.column_name == "provinces":
            value = self.widget.clean("", row=data)
            return value

        try:
            value = data[self.column_name]
        except KeyError:
            raise KeyError(
                "Column '%s' not found in dataset. Available "
                "columns are: %s" % (self.column_name, list(data))
            )

        # If ValueError is raised here, import_obj() will handle it
        value = self.widget.clean(value, row=data)

        if value in self.empty_values and self.default != NOT_PROVIDED:
            if callable(self.default):
                return self.default()
            return self.default

        return value


class InfrastructureProjectResource(resources.ModelResource):
    """
    Class to help django-import-export know how to map the rows in infrastructure project
    import files to django models.
    """

    featured = Field(
        attribute="featured", column_name="featured", widget=CustomBooleanWidget()
    )
    provinces = InfrastructureProjectProvinceField(
        attribute="provinces", column_name="provinces", widget=CustomProvinceWidget()
    )

    class Meta:
        model = models.InfrastructureProjectPart
        import_id_fields = ["project_slug", "financial_year"]

    def import_field(self, field, obj, data, is_m2m=False):
        """
        The only reason to override this function is so that we can force the
        clean() method to run on the provinces field, even though it doesn't
        exist in the import csv. The reason for this being that it doesn't seem
        like there's another easy way to 'create' a new field by using other
        fields.
        """

        if (
            field.attribute and field.column_name in data
        ) or field.attribute == "provinces":
            field.save(obj, data, is_m2m)
