from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from performance import views
from rest_framework.routers import routers
from django.urls import path, include
from .views import IndicatorViewSet

app_name = 'performance'

router = routers.DefaultRouter()
router.register('', IndicatorViewSet, basename ='user' )
urlpatterns = router.urls

""" urlpatterns = [

    path('admin/', admin.site.urls),
    path('',include(router.urls))

] """


