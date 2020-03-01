# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from slugify import slugify

from budgetportal import models
from budgetportal.json_encoder import JSONEncoder
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render
from drf_haystack.filters import (
    HaystackFacetFilter,
    HaystackFilter,
    HaystackOrderingFilter,
)
from drf_haystack.mixins import FacetMixin
from drf_haystack.serializers import HaystackFacetSerializer, HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from rest_framework import serializers
from rest_framework.views import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.settings import api_settings
from rest_framework_csv import renderers

from ..models import ProvInfraProjectSnapshot, SearchPageCSVDownloadRequest
from ..prov_infra_project.charts import time_series_data
from ..search_indexes import ProvInfraProjectIndex


def provincial_infrastructure_project_list(request):
    context = {
        "page_title": "Provincial infrastructure project search - vulekamali",
        "page_description": "Find infrastructure projects by provincial departments.",
        "page_data_json": "null",
    }
    return render(request, "webflow/infrastructure-search-template.html", context)


def provincial_infrastructure_project_detail(request, id, slug):
    project = get_object_or_404(models.ProvInfraProject, pk=int(id))
    snapshot = project.project_snapshots.latest()
    page_data = {"project": model_to_dict(snapshot)}
    page_data["project"]["irm_snapshot"] = str(snapshot.irm_snapshot)
    snapshot_list = list(project.project_snapshots.all())
    page_data["time_series_chart"] = time_series_data(snapshot_list)
    department = models.Department.get_in_latest_government(
        snapshot.department, snapshot.province
    )
    page_data["department_url"] = department.get_url_path() if department else None
    page_data["province_depts_url"] = (
        "/%s/departments?province=%s&sphere=provincial"
        % (models.FinancialYear.get_latest_year().slug, slugify(snapshot.province),)
    )
    page_data[
        "latest_snapshot_financial_year"
    ] = snapshot.irm_snapshot.financial_year.slug
    context = {
        "project": project,
        "page_data_json": json.dumps(
            page_data, cls=JSONEncoder, sort_keys=True, indent=4
        ),
        "page_title": "%s, %s Infrastructure projects - vulekamali"
        % (snapshot.name, snapshot.province),
        "page_description": "Provincial infrastructure project by the %s %s department."
        % (snapshot.province, snapshot.department),
        "download_url": project.csv_download_url
    }
    return render(
        request, "webflow/detail_provincial-infrastructure-projects.html", context
    )


class ProvInfaProjectCSVSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvInfraProjectSnapshot
        fields = "__all__"


class ProvInfaProjectCSVDownload(RetrieveAPIView):
    queryset = models.ProvInfraProject.objects.prefetch_related("project_snapshots")
    serializer_class = ProvInfaProjectCSVSnapshotSerializer
    renderer_classes = (renderers.CSVRenderer,) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)

    def get(self, request, *args, **kwargs):
        project = self.queryset.get(id=int(kwargs['id']))
        serializer = self.serializer_class(project.project_snapshots.iterator(), many=True)
        return Response(serializer.data)


class ProvInfraProjectSearchViewCSVDownload(RetrieveAPIView):
    queryset = SearchPageCSVDownloadRequest.objects.prefetch_related("projects_snapshots")
    serializer_class = ProvInfaProjectCSVSnapshotSerializer
    renderer_classes = (renderers.CSVRenderer,) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    lookup_field = "uuid"

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(obj.projects_snapshots.iterator(), many=True)
        return Response(serializer.data)


class ProvInfraProjectSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [ProvInfraProjectIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
            "id",
            "name",
            "province",
            "department",
            "status",
            "status_order",
            "primary_funding_source",
            "estimated_completion_date",
            "total_project_cost",
            "url_path",
            "latitude",
            "longitude",
        ]

    def __init__(self, *args, **kwargs):
        # https://www.django-rest-framework.org/api-guide/serializers/#example
        # Instantiate the superclass normally
        super(ProvInfraProjectSerializer, self).__init__(*args, **kwargs)

        fields = self.context["request"].query_params.get("fields")
        if fields:
            fields = fields.split(",")
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProvInfraProjectFacetSerializer(HaystackFacetSerializer):

    serialize_objects = True  # Setting this to True will serialize the
    # queryset into an `objects` list. This
    # is useful if you need to display the faceted
    # results. Defaults to False.

    class Meta:
        index_classes = [ProvInfraProjectIndex]
        fields = ["province", "department", "status", "primary_funding_source"]
        field_options = {
            "province": {},
            "department": {},
            "status": {},
            "primary_funding_source": {},
        }


class ProvInfraProjectFacetFilter(HaystackFacetFilter):
    def filter_queryset(self, request, queryset, view, *args, **kwargs):
        queryset = super(ProvInfraProjectFacetFilter, self).filter_queryset(
            request, queryset, view, *args, **kwargs
        )
        text_query = request.query_params.get("q", None)
        if text_query:
            queryset = queryset.filter(text=text_query)
        return queryset


class ProvInfraProjectFilter(HaystackFilter):
    def filter_queryset(self, request, queryset, view, *args, **kwargs):
        queryset = super(ProvInfraProjectFilter, self).filter_queryset(
            request, queryset, view, *args, **kwargs
        )
        text_query = request.query_params.get("q", None)
        if text_query:
            queryset = queryset.filter(text=text_query)
        return queryset


class ProvInfraProjectSearchView(FacetMixin, HaystackViewSet):

    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    # index_models = [Location]

    serializer_class = ProvInfraProjectSerializer
    filter_backends = [ProvInfraProjectFilter, HaystackOrderingFilter]

    facet_serializer_class = ProvInfraProjectFacetSerializer
    facet_filter_backends = [ProvInfraProjectFacetFilter]

    ordering_fields = [
        "name",
        "total_project_cost",
        "status_order",
        "estimated_completion_date",
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        csv_download_request = self._create_csv_download_request(queryset)
        response = super().list(request, *args, **kwargs)
        response.data["download_url"] = csv_download_request.download_url
        return response

    def _create_csv_download_request(self, queryset):
        ids = queryset.values_list("id", flat=True)
        csv_download_request = SearchPageCSVDownloadRequest.objects.create()
        csv_download_request.projects_snapshots.set(ProvInfraProjectSnapshot.objects.filter(id__in=ids))
        return csv_download_request