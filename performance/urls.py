from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


router = DefaultRouter()
router.register('api/v1', views.IndicatorReadOnlyModelViewSet)
#urlpatterns = router.urls

urlpatterns =[
    url('/eqprs', include(router.urls))  
]














