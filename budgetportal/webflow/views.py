# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from budgetportal import models
from ..search_indexes import ProvInfraProjectIndex

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
    return render(request, "webflow/infrastructure-project-list.html", context=context)


def provincial_infrastructure_project_detail(request, IRM_project_id, slug):
    project = get_object_or_404(
        models.ProvInfraProject, IRM_project_id=int(IRM_project_id)
    )
    page_data = {"project": model_to_dict(project)}
    context = {
        "project": project,
        "page_data_json": json.dumps(
            page_data, cls=JSONEncoder, sort_keys=True, indent=4
        ),
        "page_title": "%s, %s Infrastructure projects - vulekamali"
        % (project.name, project.province),
        "page_description": "Provincial infrastructure project by the %s %s department."
        % (project.province, project.department),
    }
    return render(
        request,
        "webflow/detail_provincial-infrastructure-projects.html",
        context=context,
    )


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
            "primary_funding_source",
            "estimated_completion_date",
            "total_project_cost",
        ]


class ProvInfraProjectSearchView(HaystackViewSet):

    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    # index_models = [Location]

    serializer_class = ProvInfraProjectSerializer
