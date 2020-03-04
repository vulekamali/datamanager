# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import urllib.parse

from copy import deepcopy
from slugify import slugify
from budgetportal import models
from budgetportal.csv_gen import Echo
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
from drf_haystack.serializers import HaystackFacetSerializer, HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView

from ..models import ProvInfraProjectSnapshot
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
        "csv_download_url": project.csv_download_url,
    }
    return render(
        request, "webflow/detail_provincial-infrastructure-projects.html", context
    )


class ProvInfraProjectCSVGeneratorMixIn:
    labels = {
        "adjustment_appropriation_construction_costs": "adjusted_appropriation_construction_costs",
        "adjustment_appropriation_total": "adjusted_appropriation_total",
        "total_project_cost": "estimated_total_project_cost",
    }

    def generate_csv_response(self, response_results, filename="export.csv"):
        response = StreamingHttpResponse(
            streaming_content=self._generate_rows(response_results),
            content_type="text/csv",
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        return response

    def _generate_rows(self, response_results):
        headers = self._get_headers(ProvInfraProjectCSVSerializer.Meta.fields)
        writer = csv.DictWriter(Echo(), fieldnames=headers)
        yield writer.writerow({h: h for h in headers})

        for row in response_results:
            prepared_row = self._prepare_row(row)
            yield writer.writerow(prepared_row)

    def _get_headers(self, headers):
        return [self.labels.get(header, header) for header in headers]

    def _prepare_row(self, row):
        prepared_row = deepcopy(row)
        for old_key, new_key in self.labels.items():
            prepared_row[new_key] = prepared_row[old_key]
            del prepared_row[old_key]
        return prepared_row


class ProvInfaProjectCSVSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvInfraProjectSnapshot
        exclude = ["created_at", "updated_at", "id", "project", "irm_snapshot"]


class ProvInfaProjectCSVDownload(RetrieveAPIView, ProvInfraProjectCSVGeneratorMixIn):
    queryset = models.ProvInfraProject.objects.prefetch_related("project_snapshots")
    serializer_class = ProvInfaProjectCSVSnapshotSerializer

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(self.queryset, id=int(kwargs["id"]))
        serializer = self.serializer_class(
            project.project_snapshots.iterator(), many=True
        )
        filename = "{}.csv".format(project.get_slug())
        return self.generate_csv_response(serializer.data, filename=filename)

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context["labels"] = self.labels
        return context


class ProvInfraProjectSerializer(HaystackSerializer):
    class Meta:
        # The `index_classes` attribute is a list of which search indexes
        # we want to include in the search.
        index_classes = [ProvInfraProjectIndex]

        # The `fields` contains all the fields we want to include.
        # NOTE: Make sure you don't confuse these with model attributes. These
        # fields belong to the search index!
        fields = [
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


class ProvInfraProjectCSVSerializer(HaystackSerializer):
    class Meta:
        index_classes = [ProvInfraProjectIndex]
        fields = [
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
            "project_number",
            "local_municipality",
            "district_municipality",
            "budget_programme",
            "nature_of_investment",
            "funding_status",
            "program_implementing_agent",
            "principle_agent",
            "main_contractor",
            "other_parties",
            "start_date",
            "estimated_construction_start_date",
            "contracted_construction_end_date",
            "estimated_construction_end_date",
            "total_professional_fees",
            "total_construction_costs",
            "variation_orders",
            "expenditure_from_previous_years_professional_fees",
            "expenditure_from_previous_years_construction_costs",
            "expenditure_from_previous_years_total",
            "project_expenditure_total",
            "main_appropriation_professional_fees",
            "adjusted_appropriation_professional_fees",
            "main_appropriation_construction_costs",
            "adjustment_appropriation_construction_costs",
            "main_appropriation_total",
            "adjustment_appropriation_total",
            "actual_expenditure_q1",
            "actual_expenditure_q2",
            "actual_expenditure_q3",
            "actual_expenditure_q4",
        ]


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


class ProvInfraProjectSearchView(
    FacetMixin, HaystackViewSet, ProvInfraProjectCSVGeneratorMixIn
):

    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    # index_models = [Location]

    serializer_class = ProvInfraProjectSerializer
    csv_serializer_class = ProvInfraProjectCSVSerializer
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
        csv_download_params = self._get_csv_query_params(request.query_params)
        response = super().list(request, *args, **kwargs)
        response.data["csv_download_url"] = reverse(
            "provincial-infrastructure-project-api-csv"
        )
        if csv_download_params:
            response.data["csv_download_url"] += "?{}".format(csv_download_params)
        return response

    @action(detail=False, methods=["get"])
    def get_csv(self, request, *args, **kwargs):
        self.serializer_class = self.csv_serializer_class
        response = super().list(request, *args, **kwargs)
        return self.generate_csv_response(
            response.data["results"], filename=self._get_filename(request.query_params)
        )

    def _get_csv_query_params(self, original_query_params):
        csv_download_params = original_query_params.copy()
        csv_download_params.pop("fields", None)
        csv_download_params.pop("limit", None)
        return urllib.parse.urlencode(csv_download_params)

    def _get_filename(self, query_params):
        keys_to_check = (
            "province",
            "department",
            "status",
            "primary_founding_source",
            "q",
        )
        extension = "csv"
        filename = "provincial-infrastructure-projects"
        for key in keys_to_check:
            if query_params.get(key):
                filename += "-{}-{}".format(key, slugify(query_params[key]))
        return "{}.{}".format(filename, extension)
