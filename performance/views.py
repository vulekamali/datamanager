from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework import generics
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from budgetportal.models import MainMenuItem
from django.contrib.postgres.search import SearchQuery
from drf_excel.mixins import XLSXFileMixin
from django.http import StreamingHttpResponse

import xlsx_streaming

FIELD_MAP = {
    "department_name": "department__name",
    "financial_year_slug": "department__government__sphere__financial_year__slug",
    "government_name": "department__government__name",
    "sphere_name": "department__government__sphere__name",
    "frequency": "frequency",
    "mtsf_outcome": "mtsf_outcome",
    "sector": "sector",
}

XLSX_COLUMNS = [
    "department__government__sphere__financial_year__slug",
    "department__government__sphere__name",
    "department__government__name",
    "department__name",
    "programme_name",
    "subprogramme_name",
    "indicator_name",
    "frequency",
    "q1_target",
    "q1_actual_output",
    "q1_deviation_reason",
    "q1_corrective_action",
    "q2_target",
    "q2_actual_output",
    "q2_deviation_reason",
    "q2_corrective_action",
    "q3_target",
    "q3_actual_output",
    "q3_deviation_reason",
    "q3_corrective_action",
    "q4_target",
    "q4_actual_output",
    "q4_deviation_reason",
    "q4_corrective_action",
    "annual_target",
    "annual_aggregate_output",
    "annual_pre_audit_output",
    "annual_deviation_reason",
    "annual_corrective_action",
    "annual_audited_output",
    "sector",
    "type",
    "subtype",
    "mtsf_outcome",
    "cluster"
]


def performance_tabular_view(request):
    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "title": "Quarterly performance reporting (QPR) indicators",
        "description": "Find the latest quarterly performance monitoring indicators, results, and explanations from national and provincial departments. How is performance measured in government? Quarterly and audited annual indicators is one of the tools to monitor implementation of department mandates.",
    }
    return render(request, "performance/performance.html", context)


def text_search(qs, text):
    if len(text) == 0:
        return qs

    print(qs)
    print(text)

    return qs.filter(content_search=SearchQuery(text))


def add_filters(qs, params):
    query_dict = {}
    for k, v in FIELD_MAP.items():
        if v in params:
            query_dict[v] = params[v]

    return qs.filter(**query_dict).distinct()


def get_filtered_queryset(queryset, request):
    search_query = request.GET.get("q", "")

    filtered_queryset = queryset.select_related(
        "department",
        "department__government",
        "department__government__sphere",
        "department__government__sphere__financial_year",
    )
    filtered_queryset = text_search(filtered_queryset, search_query)
    filtered_queryset = add_filters(filtered_queryset, request.GET)

    return filtered_queryset


class IndicatorListView(generics.ListAPIView):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
    pagination_class = PageNumberPagination

    def list(self, request):
        queryset = get_filtered_queryset(self.get_queryset(), request)

        facets = self.get_facets(queryset)

        queryset = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        data = {
            "items": serializer.data,
            "facets": facets,
        }
        return self.get_paginated_response(data)

    def get_facets(self, qs):
        def facet_query(field):
            return qs.values(field).annotate(count=Count(field))

        return {
            "department_name": facet_query("department__name"),
            "financial_year_slug": facet_query(
                "department__government__sphere__financial_year__slug"
            ),
            "government_name": facet_query("department__government__name"),
            "sphere_name": facet_query("department__government__sphere__name"),
            "frequency": facet_query("frequency"),
            "mtsf_outcome": facet_query("mtsf_outcome"),
            "sector": facet_query("sector"),
        }


class IndicatorXLSXListView(XLSXFileMixin, generics.ListAPIView):
    pagination_class = None
    template_filename = "performance/template.xlsx"
    filename = "eqprs-indicators.xlsx"
    queryset = Indicator.objects.all()

    def list(self, request, *args, **kwargs):
        excel_data = get_filtered_queryset(self.get_queryset(), request)

        with open(self.template_filename, "rb") as template:
            stream = xlsx_streaming.stream_queryset_as_xlsx(
                self.filter_queryset(excel_data).values_list(
                    *XLSX_COLUMNS
                ),
                xlsx_template=template,
                batch_size=50,
            )
        response = StreamingHttpResponse(
            stream,
            content_type="application/vnd.xlsxformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={self.filename}"
        return response
