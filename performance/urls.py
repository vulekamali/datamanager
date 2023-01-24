from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


urlpatterns =[
    path(r'api/v1/eqprs/', views.IndicatorListView.as_view()),
]
