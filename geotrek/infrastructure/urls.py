from django.conf.urls import url

from mapentity.registry import registry

from . import models
from geotrek.trekking.views import TrekInfrastructureViewSet


urlpatterns = registry.register(models.Infrastructure)
urlpatterns += [
    url(r'^api/(?P<lang>\w\w)/treks/(?P<pk>\d+)/infrastructures\.geojson$',
        TrekInfrastructureViewSet.as_view({'get': 'list'}), name="trek_infrastructure_geojson"),
]
