# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from ..models import ProvInfraProject


def provincial_infrastructure_project_list(request):
    context = {}
    return render(request, 'infrastructure-search.html', context=context)


def provincial_infrastructure_project_detail(request):
    context = {}
    return render(request, 'webflow/infrastructure-project.html', context=context)
