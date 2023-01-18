from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


router = DefaultRouter()
router.register(r'api/v1/', views.IndicatorReadOnlyModelViewSet)

urlpatterns =[
    
    path('', include(router.urls)),
    path('/eqprs', include('rest_framework.urls', namespace='rest_framework'))
   
]














