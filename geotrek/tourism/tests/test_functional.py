from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

import filecmp

from geotrek.common.factories import AttachmentFactory
from geotrek.common.tests import CommonTest
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.tourism.factories import (TouristicContentFactory,
                                       TouristicContentCategoryFactory,
                                       TouristicEventFactory)
from mapentity.factories import SuperUserFactory

from mock import patch
import os


class TouristicContentViewsTests(CommonTest):
    model = TouristicContent
    modelfactory = TouristicContentFactory
    userfactory = SuperUserFactory

    def setUp(self):
        translation.deactivate()
        super(TouristicContentViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _(u'Invalid geometry value.')

    def get_good_data(self):
        return {
            'name_fr': u'test',
            'category': TouristicContentCategoryFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }


class TouristicEventViewsTests(CommonTest):
    model = TouristicEvent
    modelfactory = TouristicEventFactory
    userfactory = SuperUserFactory

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _(u'Invalid geometry value.')

    def get_good_data(self):
        return {
            'name_fr': u'test',
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }

    @patch('mapentity.helpers.requests')
    def test_document_export_with_attachment(self, mock_requests):
        obj = self.modelfactory.create()
        attachment = AttachmentFactory.create(content_object=obj,
                                              attachment_file=get_dummy_uploaded_image(),
                                              title='mapimage')
        obj.attachment = attachment
        obj.save()
        self.login()
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = '<p id="properties">Mock</p>'
        response = self.client.get(obj.get_document_url())
        self.assertEqual(response.status_code, 200)
        element_in_dir = os.listdir(os.path.join(settings.MEDIA_ROOT, 'maps'))
        first_path = os.path.join(settings.MEDIA_ROOT, 'maps', element_in_dir[0])
        second_path = os.path.join(settings.MEDIA_ROOT, attachment.attachment_file.name)
        self.assertTrue(filecmp.cmp(first_path, second_path))
