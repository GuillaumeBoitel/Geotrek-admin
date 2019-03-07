# -*- encoding: UTF-8 -*-
from io import BytesIO
import json
from landez.sources import DownloadError
import mock
import os
import shutil
import zipfile

from django.conf import settings
from django.core import management
from django.core.management.base import CommandError
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.common.utils.testdata import get_dummy_uploaded_image_svg, get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.flatpages.factories import FlatPageFactory
from geotrek.flatpages.models import FlatPage
from geotrek.trekking.models import Trek, POI
from geotrek.trekking.factories import TrekWithPublishedPOIsFactory, PracticeFactory


class SyncMobileTilesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileTilesTest, cls).setUpClass()
        translation.deactivate()

    @mock.patch('landez.TilesManager.tile', return_value='I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles(self, mock_tileslist, mock_tiles):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output)
        zfile = zipfile.ZipFile(os.path.join('tmp', 'mobile', 'nolang', 'tiles.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("mobile/nolang/tiles.zip", output.getvalue())

    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tile_fail(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output)
        zfile = zipfile.ZipFile(os.path.join('tmp', 'mobile', 'nolang', 'tiles.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("mobile/nolang/tiles.zip", output.getvalue())

    @override_settings(MOBILE_TILES_URL=['http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                         'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'])
    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_multiple_tiles(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output)
        zfile = zipfile.ZipFile(os.path.join('tmp', 'mobile', 'nolang', 'tiles.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value='I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_with_treks(self, mock_tileslist, mock_tiles, mock_prepare):
        output = BytesIO()
        portal_a = TargetPortalFactory()
        portal_b = TargetPortalFactory()
        trek = TrekWithPublishedPOIsFactory.create(published=True)
        trek_not_same_portal = TrekWithPublishedPOIsFactory.create(published=True, portals=(portal_a, ))
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output,
                                portal=portal_b.name)

        zfile_global = zipfile.ZipFile(os.path.join('tmp', 'mobile', 'nolang', 'tiles.zip'))
        for finfo in zfile_global.infolist():
            ifile_global = zfile_global.open(finfo)
            self.assertEqual(ifile_global.readline(), 'I am a png')
        zfile_trek = zipfile.ZipFile(os.path.join('tmp', 'mobile', 'nolang', str(trek.pk), 'tiles.zip'))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            self.assertEqual(ifile_trek.readline(), 'I am a png')
        self.assertIn("mobile/nolang/tiles.zip", output.getvalue())
        self.assertIn("mobile/nolang/{pk}/tiles.zip".format(pk=trek.pk), output.getvalue())

        self.assertFalse(os.path.exists(os.path.join('tmp', 'mobile', 'nolang', str(trek_not_same_portal.pk),
                                                     'tiles.zip')))

    def tearDown(self):
        shutil.rmtree('tmp')


class SyncMobileFailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileFailTest, cls).setUpClass()
        translation.deactivate()

    def test_fail_directory_not_empty(self):
        os.makedirs(os.path.join('tmp', 'other'))
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertEqual(e.exception.message, "Destination directory contains extra data")
        shutil.rmtree(os.path.join('tmp', 'other'))

    def test_fail_url_ftp(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_mobile', 'tmp', url='ftp://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertEqual(e.exception.message, "url parameter should start with http:// or https://")

    def test_language_not_in_db(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, languages='cat', verbosity=2)
        self.assertEqual(e.exception.message,
                         "Language cat doesn't exist. Select in these one : ('en', 'es', 'fr', 'it')")

    def test_attachments_missing_from_disk(self):
        trek_1 = TrekWithPublishedPOIsFactory.create(published_fr=True)
        attachment = AttachmentFactory(content_object=trek_1, attachment_file=get_dummy_uploaded_image())
        os.remove(attachment.attachment_file.path)
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, languages='fr', verbosity=2, stdout=BytesIO())
        self.assertFalse(os.path.exists(os.path.join('tmp', 'mobile', 'nolang', 'media', 'trekking_trek')))

    @classmethod
    def tearDownClass(cls):
        super(SyncMobileFailTest, cls).tearDownClass()
        shutil.rmtree('tmp')


class SyncMobileSpecificOptionsTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileSpecificOptionsTest, cls).setUpClass()
        FlatPageFactory.create(published_fr=True)
        FlatPageFactory.create(published_en=True)

    def test_lang(self):
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=0, languages='fr')
        with open(os.path.join('tmp', 'mobile', 'fr', 'flatpages.json'), 'r') as f:
            flatpages = json.load(f)
            self.assertEquals(len(flatpages), 1)
        with self.assertRaises(IOError):
            open(os.path.join('tmp', 'mobile', 'en', 'flatpages.json'), 'r')


class SyncMobileFlatpageTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileFlatpageTest, cls).setUpClass()
        translation.deactivate()

        cls.portals = []

        cls.portal_a = TargetPortalFactory()
        cls.portal_b = TargetPortalFactory()

        cls.source_a = RecordSourceFactory()
        cls.source_b = RecordSourceFactory()

        FlatPageFactory.create(published=True)
        FlatPageFactory.create(portals=(cls.portal_a, cls.portal_b),
                               published=True)
        FlatPageFactory.create(published=True)
        FlatPageFactory.create(portals=(cls.portal_a,),
                               published=True)

    def test_sync_flatpage(self):
        '''
        Test synced flatpages
        '''
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'flatpages.json'), 'r') as f:
                flatpages = json.load(f)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(**{'published_{}'.format(lang): True}).count())
        self.assertIn('mobile/en/flatpages.json', output.getvalue())

    def test_sync_filtering_portal(self):
        '''
        Test if synced flatpages are filtered by portal
        '''
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                portal=self.portal_b.name, skip_tiles=True, verbosity=2, stdout=output)
        with open(os.path.join('tmp', 'mobile/fr/flatpages.json'), 'r') as f_file:
            flatpages = json.load(f_file)
            self.assertEquals(len(flatpages), 0)
        with open(os.path.join('tmp', 'mobile/en/flatpages.json'), 'r') as f_file:
            flatpages = json.load(f_file)
            self.assertEquals(len(flatpages), 3)
        self.assertIn('mobile/en/flatpages.json', output.getvalue())

    def test_sync_flatpage_lang(self):
        output = BytesIO()
        FlatPageFactory.create(published_fr=True)
        FlatPageFactory.create(published_en=True)
        FlatPageFactory.create(published_es=True)
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'flatpages.json'), 'r') as f:
                flatpages = json.load(f)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(**{'published_{}'.format(lang): True}).count())
        self.assertIn('mobile/en/flatpages.json', output.getvalue())

    def test_sync_flatpage_content(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'flatpages.json'), 'r') as f:
                flatpages = json.load(f)
                self.assertEquals(len(flatpages),
                                  FlatPage.objects.filter(**{'published_{}'.format(lang): True}).count())
        self.assertIn('mobile/en/flatpages.json', output.getvalue())

    @classmethod
    def tearDownClass(cls):
        super(SyncMobileFlatpageTest, cls).tearDownClass()
        shutil.rmtree('tmp')


class SyncMobileSettingsTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileSettingsTest, cls).setUpClass()
        translation.deactivate()

    def test_sync_settings(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'settings.json'), 'r') as f:
                settings_json = json.load(f)
                self.assertEquals(len(settings_json), 2)
                self.assertEqual(len(settings_json['data']), 11)

        self.assertIn('mobile/en/settings.json', output.getvalue())

    def test_sync_settings_with_picto_svg(self):
        output = BytesIO()
        practice = PracticeFactory.create(pictogram=get_dummy_uploaded_image_svg())
        pictogram_png = practice.pictogram.url.replace('.png', '.svg')
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'settings.json'), 'r') as f:
                settings_json = json.load(f)
                self.assertEquals(len(settings_json), 2)
                self.assertEqual(len(settings_json['data']), 11)
                self.assertEqual(settings_json['data'][3]['values'][0]['pictogram'], pictogram_png)
        self.assertIn('mobile/en/settings.json', output.getvalue())

    @classmethod
    def tearDownClass(cls):
        super(SyncMobileSettingsTest, cls).tearDownClass()
        shutil.rmtree('tmp')


class SyncMobileTreksTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncMobileTreksTest, cls).setUpClass()
        cls.trek_1 = TrekWithPublishedPOIsFactory()
        cls.trek_2 = TrekWithPublishedPOIsFactory()
        cls.attachment_1 = AttachmentFactory.create(content_object=cls.trek_1,
                                                    attachment_file=get_dummy_uploaded_image())
        cls.poi_1 = POI.objects.first()
        cls.attachment_poi_image_1 = AttachmentFactory.create(content_object=cls.poi_1,
                                                              attachment_file=get_dummy_uploaded_image())
        cls.attachment_poi_image_2 = AttachmentFactory.create(content_object=cls.poi_1,
                                                              attachment_file=get_dummy_uploaded_image())
        cls.attachment_poi_file = AttachmentFactory.create(content_object=cls.poi_1,
                                                           attachment_file=get_dummy_uploaded_file())
        translation.deactivate()

    def test_sync_treks(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with open(os.path.join('tmp', 'mobile', lang, 'treks.geojson'), 'r') as f:
                trek_geojson = json.load(f)
                self.assertEqual(len(trek_geojson['features']),
                                 Trek.objects.filter(**{'published_{}'.format(lang): True}).count())

        self.assertIn('mobile/en/treks.geojson', output.getvalue())

    def test_sync_treks_by_pk(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        with open(os.path.join('tmp', 'mobile', 'en', 'treks',
                               '{pk}.geojson'.format(pk=str(self.trek_1.pk))), 'r') as f:
            trek_geojson = json.load(f)
            self.assertEqual(len(trek_geojson['properties']), 28)

        self.assertIn('mobile/en/treks/{pk}.geojson'.format(pk=str(self.trek_1.pk)), output.getvalue())

    def test_sync_pois_by_treks(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        with open(os.path.join('tmp', 'mobile', 'en', 'treks', str(self.trek_1.pk), 'pois.geojson'), 'r') as f:
            trek_geojson = json.load(f)
            self.assertEqual(len(trek_geojson['features']), 2)

        self.assertIn('mobile/en/treks/{pk}/pois.geojson'.format(pk=str(self.trek_1.pk)), output.getvalue())

    def test_medias_treks(self):
        output = BytesIO()
        management.call_command('sync_mobile', 'tmp', url='http://localhost:8000',
                                skip_tiles=True, verbosity=2, stdout=output)
        self.assertTrue(os.path.exists(os.path.join('tmp', 'mobile', 'nolang', str(self.trek_1.pk), 'media',
                                                    'paperclip', 'trekking_poi')))
        self.assertTrue(os.path.exists(os.path.join('tmp', 'mobile', 'nolang', str(self.trek_1.pk), 'media',
                                                    'paperclip', 'trekking_trek')))

    @classmethod
    def tearDownClass(cls):
        super(SyncMobileTreksTest, cls).tearDownClass()
        shutil.rmtree('tmp')
