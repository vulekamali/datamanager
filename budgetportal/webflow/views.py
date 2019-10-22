# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from budgetportal.webflow.serializers import ProvInfraProjectSerializer
from ..models import ProvInfraProject
import json
import decimal
import datetime


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def provincial_infrastructure_project_list(request):
    projects = ProvInfraProject.objects.all()
    context = {"projects": projects}
    return render(request, "webflow/infrastructure-project-list.html", context=context)


def provincial_infrastructure_project_detail(request, IRM_project_id, slug):
    project = get_object_or_404(ProvInfraProject, IRM_project_id=int(IRM_project_id))
    page_data = {"project": model_to_dict(project)}
    context = {
        "project": project,
        "page_data_json": json.dumps(
            page_data, cls=JSONEncoder, sort_keys=True, indent=4
        ),
    }
    return render(
        request,
        "webflow/detail_provincial-infrastructure-projects.html",
        context=context,
    )


class ProvInfraProjectView(generics.ListAPIView):
    queryset = ProvInfraProject.objects.all()
    serializer_class = ProvInfraProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ["province", "department", "status", "primary_funding_source"]
    search_fields = [
        "name",
        "district_municipality",
        "local_municipality",
        "province",
        "main_contractor",
        "principle_agent",
        "program_implementing_agent",
        "other_parties",
    ]

    def list(self, request, *args, **kwargs):
        base_url = (
            get_current_site(request).domain + "/infrastructure-projects/provincial/"
        )
        project_urls = []

        queryset = self.filter_queryset(self.get_queryset())
        for project in queryset:
            project_urls.append(project.get_url_path())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_list = serializer.data
            for index, response in enumerate(response_list):
                url = base_url + project_urls[index]
                response.update({"url": url})
            return self.get_paginated_response(response_list)

        serializer = self.get_serializer(queryset, many=True)
        response_list = serializer.data
        for index, response in enumerate(response_list):
            url = base_url + project_urls[index]
            response.update({"url": url})

        return Response(response_list)
