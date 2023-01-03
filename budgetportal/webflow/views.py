# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import urllib.parse

from slugify import slugify

from budgetportal import models
from budgetportal.csv_gen import Echo
from budgetportal.infra_projects.charts import time_series_data
from budgetportal.json_encoder import JSONEncoder
from django.forms.models import model_to_dict
from django.http.response import StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from drf_haystack.filters import (
    HaystackFacetFilter,
    HaystackFilter,
    HaystackOrderingFilter,
)
from drf_haystack.mixins import FacetMixin
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView

from .serializers import (
    InfaProjectCSVSnapshotSerializer,
    InfraProjectCSVSerializer,
    InfraProjectFacetSerializer,
    InfraProjectSerializer,
)


def infrastructure_project_list(request):
    context = {
        "page_title": "Infrastructure project search - vulekamali",
        "page_description": "Find infrastructure projects run by national and provincial government.",
        "page_data_json": "null",
    }
    return render(request, "webflow/infrastructure-search-template.html", context)


def infrastructure_project_detail(request, id, slug):
    project = get_object_or_404(models.InfraProject, pk=int(id))
    snapshot = project.project_snapshots.latest()
    page_data = {"project": model_to_dict(snapshot)}
    page_data["project"]["irm_snapshot"] = str(snapshot.irm_snapshot)
    page_data["project"]["csv_download_url"] = project.csv_download_url
    snapshot_list = list(project.project_snapshots.all())
    page_data["time_series_chart"] = time_series_data(snapshot_list)
    department = models.Department.get_in_latest_government(
        snapshot.department, snapshot.government
    )

    page_data["department_url"] = department.get_url_path() if department else None
    page_data[
        "province_depts_url"
    ] = "/%s/departments?province=%s&sphere=provincial" % (
        models.FinancialYear.get_latest_year().slug,
        slugify(snapshot.province),
    )
    page_data[
        "latest_snapshot_financial_year"
    ] = snapshot.irm_snapshot.sphere.financial_year.slug
    context = {
        "project": project,
        "page_data_json": json.dumps(
            page_data, cls=JSONEncoder, sort_keys=True, indent=4
        ),
        "page_title": "%s, %s Infrastructure projects - vulekamali"
        % (snapshot.name, snapshot.province),
        "page_description": "Infrastructure project by the %s %s department."
        % (snapshot.government_label, snapshot.department),
    }
    return render(request, "webflow/detail_infrastructure-projects.html", context)


class InfraProjectCSVGeneratorMixIn:
    def generate_csv_response(self, response_results, filename="export.csv"):
        response = StreamingHttpResponse(
            streaming_content=self._generate_rows(response_results),
            content_type="text/csv",
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response

    def _generate_rows(self, response_results):
        headers = InfraProjectCSVSerializer.Meta.fields
        writer = csv.DictWriter(Echo(), fieldnames=headers)
        yield writer.writerow({h: h for h in headers})

        for row in response_results:
            yield writer.writerow(row)


class InfaProjectCSVDownload(RetrieveAPIView, InfraProjectCSVGeneratorMixIn):
    queryset = models.InfraProject.objects.prefetch_related("project_snapshots")
    serializer_class = InfaProjectCSVSnapshotSerializer

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(self.queryset, id=int(kwargs["id"]))
        serializer = self.serializer_class(
            project.project_snapshots.iterator(), many=True
        )
        filename = "{}.csv".format(project.get_slug())
        return self.generate_csv_response(serializer.data, filename=filename)


class InfraProjectFacetFilter(HaystackFacetFilter):
    def filter_queryset(self, request, queryset, view, *args, **kwargs):
        queryset = super(InfraProjectFacetFilter, self).filter_queryset(
            request, queryset, view, *args, **kwargs
        )
        text_query = request.query_params.get("q", None)
        if text_query:
            queryset = queryset.filter(text=text_query)
        return queryset


class InfraProjectFilter(HaystackFilter):
    def filter_queryset(self, request, queryset, view, *args, **kwargs):
        queryset = super(InfraProjectFilter, self).filter_queryset(
            request, queryset, view, *args, **kwargs
        )
        text_query = request.query_params.get("q", None)
        if text_query:
            queryset = queryset.filter(text=text_query)
        return queryset


class InfraProjectSearchView(
    FacetMixin, HaystackViewSet, InfraProjectCSVGeneratorMixIn
):

    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    # index_models = [Location]

    serializer_class = InfraProjectSerializer
    csv_serializer_class = InfraProjectCSVSerializer
    filter_backends = [InfraProjectFilter, HaystackOrderingFilter]

    facet_serializer_class = InfraProjectFacetSerializer
    facet_filter_backends = [InfraProjectFacetFilter]

    ordering_fields = [
        "name",
        "estimated_total_project_cost",
        "status_order",
        "estimated_completion_date",
    ]

    def list(self, request, *args, **kwargs):
        csv_download_params = self._get_csv_query_params(request.query_params)
        response = super().list(request, *args, **kwargs)
        if isinstance(response.data, dict):
            response.data["csv_download_url"] = reverse(
                "infrastructure-project-api-csv"
            )
        if csv_download_params:
            response.data["csv_download_url"] += "?{}".format(csv_download_params)
        return response

    @action(detail=False, methods=["get"])
    def get_csv(self, request, *args, **kwargs):
        self.serializer_class = self.csv_serializer_class
        self.pagination_class = None
        response = super().list(request, *args, **kwargs)
        return self.generate_csv_response(
            response.data, filename=self._get_filename(request.query_params)
        )

    def _get_csv_query_params(self, original_query_params):
        csv_download_params = original_query_params.copy()
        csv_download_params.pop("fields", None)
        csv_download_params.pop("limit", None)
        csv_download_params.pop("offset", None)
        return urllib.parse.urlencode(csv_download_params)

    def _get_filename(self, query_params):
        keys_to_check = (
            "government_label",
            "sector",
            "province",
            "department",
            "status",
            "primary_founding_source",
            "q",
        )
        extension = "csv"
        filename = "infrastructure-projects"
        for key in keys_to_check:
            if query_params.get(key):
                filename += "-{}-{}".format(key, slugify(query_params[key]))
        return "{}.{}".format(filename, extension)
