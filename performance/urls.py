from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


router = DefaultRouter()
router.register('eqprs', views.IndicatorReadOnlyModelViewSet)
#urlpatterns = router.urls

urlpatterns =[
    url('api/v1', include(router.urls))  
]














