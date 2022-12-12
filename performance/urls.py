from django.contrib import admin
from django.conf.urls import url
from performance import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from .views import IndicatorViewSet


router = DefaultRouter()
router.register('/indicator', IndicatorViewSet)
#urlpatterns = router.urls

urlpatterns =[

    #path('admin/', admin.site.urls),
    path('/api/v1/eqprs',include(router.urls))
   

]


