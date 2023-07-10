from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views

urlpatterns = [
    # IYM
    path("", views.performance_tabular_view, name="iym"),
]
