from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from performance import views
from rest_framework import routers
from django.urls import include

router = routers.DefaultRouter()
router.register('Indicator', views.IndicatorViewSet)

urlpatterns = [

    path('admin/', admin.site.urls),
    path('',include(router.urls))

]


