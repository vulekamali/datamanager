from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


router = DefaultRouter()
router.register(r'/eqprs', views.IndicatorReadOnlyModelViewSet)

urlpatterns =[
   # url('api/v1', include(router.urls))  

    path('', include(router.urls)),
    path('api/v1/', include('rest_framework.urls', namespace='rest_framework'))
]














