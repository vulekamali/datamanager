# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
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
