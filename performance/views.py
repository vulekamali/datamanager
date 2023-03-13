from django.shortcuts import render
from .models import Indicator
from .serializer import IndicatorSerializer
from rest_framework import generics
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from budgetportal.models import MainMenuItem
from django.contrib.postgres.search import SearchQuery


def performance_tabular_view(request):
    context = {
        "navbar": MainMenuItem.objects.prefetch_related("children").all(),
        "title": "Quarterly performance reporting (QPR) indicators",
        "description": "Find the latest quarterly performance monitoring indicators, results, and explanations from national and provincial departments. How is performance measured in government? Quarterly and audited annual indicators is one of the tools to monitor implementation of department mandates.",
    }
    return render(request, "performance/performance.html", context)


class IndicatorListView(generics.ListAPIView):
    serializer_class = IndicatorSerializer
    queryset = Indicator.objects.all()
    pagination_class = PageNumberPagination

    fieldmap = {
        "department_name": "department__name",
        "financial_year_slug": "department__government__sphere__financial_year__slug",
        "government_name": "department__government__name",
        "sphere_name": "department__government__sphere__name",
        "frequency": "frequency",
        "mtsf_outcome": "mtsf_outcome",
        "sector": "sector",
    }

    def list(self, request):
        search_query = request.GET.get("q", "")

        queryset = self.get_queryset()
        queryset = self.text_search(queryset, search_query)
        queryset = self.add_filters(queryset, request.GET, self.fieldmap)

        facets = self.get_facets(queryset)

        queryset = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        data = {
            "items": serializer.data,
            "facets": facets,
        }
        return self.get_paginated_response(data)

    def text_search(self, qs, text):
        if len(text) == 0:
            return qs

        return qs.filter(content_search=SearchQuery(text))

    def add_filters(self, qs, params, filter_map):
        query_dict = {}
        for k, v in filter_map.items():
            if v in params:
                query_dict[v] = params[v]

        return qs.filter(**query_dict).distinct()

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
