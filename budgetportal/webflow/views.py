# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import SearchFilter
from budgetportal.webflow.serializers import ProvInfraProjectSnapshotSerializer
from ..models import ProvInfraProjectSnapshot, ProvInfraProject
from django.db.models import Subquery, OuterRef, Max, Prefetch

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
    latest_snapshots = ProvInfraProjectSnapshot.objects.filter(
        project=Subquery(
            (
                ProvInfraProjectSnapshot.objects.filter(
                    project=OuterRef("project"), status="Tender"
                )
                .values("project")
                .annotate(latest_snapshot=Max("project"))
                .values("latest_snapshot")[:1]
            )
        )
    )
    # hottest_cakes = Cake.objects.filter(
    #    baked_at=Subquery(
    #        (Cake.objects
    #            .filter(bakery=OuterRef('bakery'))
    #            .values('bakery')
    #            .annotate(last_bake=Max('baked_at'))
    #            .values('last_bake')[:1]
    #        )
    #    )
    # )
    # bakeries = Bakery.objects.all().prefetch_related(
    #     Prefetch('cake_set',
    #         queryset=hottest_cakes,
    #         to_attr='hottest_cakes'
    #     )
    # )
    # for bakery in bakeries:
    #    print 'Bakery %s has %s hottest_cakes' % (bakery, len(bakery.hottest_cakes))
    projects = ProvInfraProject.objects.all().prefetch_related(
        Prefetch(
            "project_snapshots", queryset=latest_snapshots, to_attr="latest_snapshots"
        )
    )
    context = {"projects": projects}
    return render(request, "webflow/infrastructure-project-list.html", context=context)


def provincial_infrastructure_project_detail(request, IRM_project_id, slug):
    project = get_object_or_404(
        ProvInfraProjectSnapshot, IRM_project_id=int(IRM_project_id)
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


class ProvInfraProjectView(generics.ListAPIView):
    queryset = ProvInfraProject.objects.all()
    serializer_class = ProvInfraProjectSnapshotSerializer
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
