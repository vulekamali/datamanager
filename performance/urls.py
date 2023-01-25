from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


urlpatterns =[
    # Performance
    path('', views.performance_tabular_view, name="performance"),
    path(r'api/v1/eqprs/', views.IndicatorListView.as_view()),
]
