from django.contrib import admin
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from performance import views


router = DefaultRouter()
<<<<<<< HEAD
router.register('api/v1/eqprs', views.IndicatorReadOnlyModelViewSet)

urlpatterns =[

    path('', include(router.urls))
=======
router.register(r'eqprs', views.IndicatorReadOnlyModelViewSet)

urlpatterns =[
    path('api/v1/', include(router.urls)),
>>>>>>> eqprs-api
]
