from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import response
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.mobile.serializers import common as api_serializers
from geotrek.flatpages.models import FlatPage
from geotrek.trekking.models import DifficultyLevel, Practice, Accessibility, Route, Theme, TrekNetwork, POIType
from geotrek.tourism.models import (InformationDeskType, TouristicContentType, TouristicEventType,
                                    TouristicContentCategory)
from geotrek.zoning.models import City


class SettingsView(APIView):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        filters = []
        if 'difficulty' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "difficulty",
                "type": "contains",
                "showAllLabel": _("Show all difficulties"),
                "hideAllLabel": _("Hide all difficulties")
            })
        if 'lengths' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "lengths",
                "type": "interval",
                "showAllLabel": _("Show all lengths"),
                "hideAllLabel": _("Hide all lengths")
            })
        if 'cities' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "cities",
                "type": "contains",
                "showAllLabel": _("Show all cities"),
                "hideAllLabel": _("Hide all cities")
            })
        if 'accessibilities' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "accessibilities",
                "type": "contains",
                "showAllLabel": _("Show all accessibilities"),
                "hideAllLabel": _("Hide all accessibilities")
            })
        if 'practice' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "practice",
                "type": "contains",
                "showAllLabel": _("Show all practices"),
                "hideAllLabel": _("Hide all practices")
            })
        if 'durations' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "durations",
                "type": "interval",
                "showAllLabel": _("Show all durations"),
                "hideAllLabel": _("Hide all durations")
            })
        if 'themes' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "themes",
                "type": "contains",
                "showAllLabel": _("Show all themes"),
                "hideAllLabel": _("Hide all themes")
            })
        if 'route' in settings.ENABLED_MOBILE_FILTERS:
            filters.append({
                "id": "route",
                "type": "contains",
                "showAllLabel": _("Show all routes"),
                "hideAllLabel": _("Hide all routes")
            })
        return response.Response({
            'filters': filters,
            'data': [
                {
                    'id': 'length',
                    'name': _('Length'),
                    'values': [
                        {"id": 1, "name": "< 10 km", "interval": [0, 9999]},
                        {"id": 2, "name": "10 - 30", "interval": [9999, 29999]},
                        {"id": 3, "name": "30 - 50", "interval": [30000, 50000]},
                        {"id": 4, "name": "> 50 km", "interval": [50000, 999999]}
                    ]

                },
                {
                    'id': 'duration',
                    'name': _('Duration'),
                    'values': [
                        {"id": 1, "name": "< 1 heure", "interval": [0, 1]},
                        {"id": 2, "name": "1h - 2h30", "interval": [1, 2.5]},
                        {"id": 3, "name": "2h30 - 5h", "interval": [2.5, 5]},
                        {"id": 4, "name": "5h - 9h", "interval": [5, 9]},
                        {"id": 5, "name": "> 9h", "interval": [9, 9999999]}
                    ]

                },
                {
                    'id': 'difficulty',
                    'name': _('Difficulty'),
                    'values': api_serializers.DifficultySerializer(DifficultyLevel.objects.all().order_by('pk'),
                                                                   many=True,
                                                                   context={'request': request}).data
                },
                {
                    'id': 'practice',
                    'name': _('Practice'),
                    'values': api_serializers.PracticeSerializer(Practice.objects.all().order_by('pk'),
                                                                 many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'accessibilities',
                    'name': _('Accessibilities'),
                    'values': api_serializers.AccessibilitySerializer(Accessibility.objects.all().order_by('pk'),
                                                                      many=True, context={'request': request}).data,
                },
                {
                    'id': 'route',
                    'name': _('Route'),
                    'values': api_serializers.RouteSerializer(Route.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'themes',
                    'name': _('Themes'),
                    'values': api_serializers.ThemeSerializer(Theme.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'networks',
                    'name': _('Networks'),
                    'values': api_serializers.NetworkSerializer(TrekNetwork.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'information_desk_types',
                    'name': _('Information Desks Types'),
                    'values': api_serializers.InformationDeskTypeSerializer(InformationDeskType.objects.all()
                                                                            .order_by('pk'),
                                                                            many=True,
                                                                            context={'request': request}).data,
                },
                {
                    'id': 'cities',
                    'name': _('Cities'),
                    'values': api_serializers.CitySerializer(City.objects.all().order_by('pk'), many=True,
                                                             context={'request': request}).data
                },
                {
                    'id': 'poi_types',
                    'name': _('POI types'),
                    'values': api_serializers.POITypeSerializer(POIType.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'touristiccontent_types',
                    'name': _('Touristic content types'),
                    'values': api_serializers.TouristicContentTypeSerializer(
                        TouristicContentType.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
                {
                    'id': 'touristicevent_types',
                    'name': _('Touristic event types'),
                    'values': api_serializers.TouristicEventTypeSerializer(
                        TouristicEventType.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
                {
                    'id': 'touristiccontent_categories',
                    'name': _('Touristic event types'),
                    'values': api_serializers.TouristicContentCategorySerializer(
                        TouristicContentCategory.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
            ]
        })


class FlatPageViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = api_serializers.FlatPageListSerializer
    serializer_detail_class = api_serializers.FlatPageDetailSerializer

    def get_queryset(self, *args, **kwargs):
        qs = FlatPage.objects.filter(target__in=['mobile', 'all'], published=True).order_by('order')
        if self.request.GET.get('portal', '') != '':
            qs = qs.filter(Q(portal__name__in=self.request.GET['portal'].split(',')) | Q(portal=None))
        return qs
