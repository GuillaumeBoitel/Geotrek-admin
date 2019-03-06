import os
import json
import mock
import shutil
from django.test import TestCase
from django.core import management

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.trekking.factories import TrekFactory
from geotrek.trekking import models as trek_models


class SyncTest(TestCase):
    def setUp(self):
        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()

        self.trek_1 = TrekFactory.create(sources=(self.source_a, ),
                                         portals=(self.portal_b,),
                                         published=True)
        self.trek_2 = TrekFactory.create(sources=(self.source_b,),
                                         published=True)
        self.trek_3 = TrekFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True)
        self.trek_4 = TrekFactory.create(portals=(self.portal_a,),
                                         published=True)

    def test_sync(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True).count())

    def test_sync_2028(self):
        self.trek_1.description = u'toto\u2028tata'
        self.trek_1.save()
        self.trek_2.delete()
        self.trek_3.delete()
        self.trek_4.delete()
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEquals(treks['features'][0]['properties']['description'], u'toto\ntata')

    def test_sync_filtering_sources(self):
        # source A only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # only 1 trek in Source A
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True,
                                                                  source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_portals(self):
        # portal B only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # only 2 treks in Portal B + 1 without portal specified
                self.assertEquals(len(treks['features']), 3)

        # portal A and B
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    portal='{},{}'.format(self.portal_a.name, self.portal_b.name),
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # 4 treks have portal A or B or no portal
                self.assertEquals(len(treks['features']), 4)

    def tearDown(self):
        shutil.rmtree('tmp')
