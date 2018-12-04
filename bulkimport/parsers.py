# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import InternalError
from django.utils.translation import ugettext as _
from geotrek.common.parsers import Parser, AttachmentParserMixin, ValueImportError, GlobalImportError
from geotrek.core.helpers import TopologyHelper
from geotrek.tourism.models import TouristicContent
from geotrek.trekking.models import POI, POIType


class XmlParser(Parser):
    ns = {}
    root = ''

    def get_part(self, dst, src, val):
        return val.findtext(src, None, self.ns)

    def next_row(self):
        if self.filename:
            with open(self.filename) as f:
                tree = ET.fromstring(f.read())
        else:
            response = requests.get(self.url, params={})
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(
                    url=self.url, status_code=response.status_code))
            tree = ET.fromstring(response.content)
        entries = tree.findall(self.root, self.ns)
        self.nb = len(entries)
        for entry in entries:
            yield entry

    def normalize_field_name(self, name):
        return name


class LeiParser(AttachmentParserMixin, XmlParser):
    root = 'Resultat/sit_liste'
    model = TouristicContent
    eid = 'eid'
    delete = True
    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': 'COMMENTAIRE',
        'contact': ('ADRPROD_NUM_VOIE', 'ADRPROD_LIB_VOIE', 'ADRPROD_CP', 'ADRPROD_LIBELLE_COMMUNE', 'ADRPROD_TEL',
                    'ADRPROD_TEL2', 'ADRPREST_TEL', 'ADRPREST_TEL2'),
        'email': ('ADRPROD_EMAIL', 'ADRPREST_EMAIL'),
        'website': ('ADRPROD_URL', 'ADRPREST_URL'),
        'geom': ('LATITUDE', 'LONGITUDE'),
    }
    category = None
    type1 = None
    non_fields = {
        'attachments': ('CRITERES/Crit[@CLEF_CRITERE="1900421"]', 'CRITERES/Crit[@CLEF_CRITERE="1900480"]'),
    }
    constant_fields = {
        'published': True,
    }
    natural_keys = {
        'category': 'label',
    }

    def __init__(self, *args, **kwargs):
        XmlParser.__init__(self, *args, **kwargs)
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1:
            self.constant_fields['type1'] = self.type1

    def start(self):
        super(LeiParser, self).start()
        lei = set(self.model.objects.filter(eid__startswith='LEI').values_list('pk', flat=True))
        self.to_delete = self.to_delete & lei

    def filter_eid(self, src, val):
        return 'LEI' + val

    def filter_attachments(self, src, val):
        (url, legend) = val
        if not url:
            return []
        url = url.replace('https://', 'http://')
        if url[:7] != 'http://':
            url = 'http://' + url
        return [(url, legend, '')]

    def filter_description(self, src, val):
        val = val.replace('\n', '<br>')
        return val

    def filter_geom(self, src, val):
        lat, lng = val
        lat = lat.replace(',', '.')
        lng = lng.replace(',', '.')
        if lat is None or lng is None:
            return None
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        try:
            geom.transform(settings.SRID)
        except InternalError as e:
            raise ValueImportError(unicode(e))
        if self.obj.geom and abs(geom.x - self.obj.geom.x) < 0.001 and abs(geom.y - self.obj.geom.y) < 0.001:
            return self.obj.geom
        return geom

    def filter_contact(self, src, val):
        (num, voie, cp, commune, tel1, tel2, tel3, tel4) = val
        val = num or u""
        if num and voie:
            val += u" "
        val += voie or u""
        if num or voie:
            val += u"<br>"
        val += cp
        if cp and commune:
            val += u" "
        val += commune or u""
        if cp or commune:
            val += u"<br>"
        if tel1:
            val += u"Tél. : " + tel1 + u"<br>"
        if tel2:
            val += u"Tél. : " + tel2 + u"<br>"
        if tel3:
            val += u"Tél. : " + tel3 + u"<br>"
        if tel4:
            val += u"Tél. : " + tel4 + u"<br>"
        return val

    def filter_website(self, src, val):
        (val1, val2) = val
        if val1:
            return 'http://' + val1
        if val2:
            return 'http://' + val2

    def filter_email(self, src, val):
        (val1, val2) = val
        return val1 or val2


class LeiHebergementParser(LeiParser):
    label = u"LEI - Hébergement"
    url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000002_pnrvn_hebergements.xml'
    category = u"Hébergement Rando+"


class LeiActivitesParser(LeiParser):
    label = u"LEI - Activités / lieux à visiter"
    url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000003_pnrvn_lieux_activites.xml'
    category = u"Activités Rando+"


# class LeiCommercesParser(LeiParser):
#     label = u"LEI - Commerces et services"
#     url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000004_pnrvn_services_commerces.xml'
#     category = u"Commerces"


# Pour les événements
# http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000005_pnrvn_manifestations.xml


class SitlorParser(LeiParser):
    label = "SITLOR"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=233&pwkey=4dc5b1e31e5e8bf0d22810a9e5e8bbc8&urlnames=tous&PVALUES=4000001,25/04/2017%2000:00:00,20/04/2018%2023:59:59,MOSELLE,2,853000026,853000077&PNAMES=elgendro,validaddu,validadau,elsector,utilisador,elcriterio0,modalidad0&lesvalid=@|@+12M&clause=233000264'
    category = u"Hébergement Rando+"
    non_fields = {
        'attachments': ('CRITERES/Crit[@CLEF_CRITERE="736000294"]', 'CRITERES/Crit[@CLEF_CRITERE="736001119"]'),
    }

    def __init__(self, *args, **kwargs):
        super(SitlorParser, self).__init__(*args, **kwargs)
#        self.fields['category'] = 'TYPE_DE_PRODUIT'

    def start(self):
        super(SitlorParser, self).start()
        sitlor = set(self.model.objects.filter(eid__startswith='LOR').values_list('pk', flat=True))
        self.to_delete = self.to_delete & sitlor

    def filter_eid(self, src, val):
        return 'LOR' + val


class LeiPOIParser(LeiParser):
    model = POI

    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': (
            'COMMENTAIRE', (
                'ADRPROD_NUM_VOIE',
                'ADRPROD_LIB_VOIE',
                'ADRPROD_CP',
                'ADRPROD_LIBELLE_COMMUNE',
                'ADRPROD_TEL',
                'ADRPROD_TEL2',
                'ADRPREST_TEL',
                'ADRPREST_TEL2'
            ), (
                'ADRPROD_EMAIL',
                'ADRPREST_EMAIL'
            ), ('ADRPROD_URL',
                'ADRPREST_URL')
        ),
        'type': 'TYPE_DE_PRODUIT',
        'geom': ('LATITUDE', 'LONGITUDE'),
    }

    natural_keys = {
        'type': 'label',
    }

    # Don't publish by default but keep published if published manually
    constant_fields = {}

    def filter_type(self, src, val):
        try:
            return self.obj.type
        except POIType.DoesNotExist:
            return super(LeiPOIParser, self).apply_filter('type', src, val)

    def parse_obj(self, row, operation):
        super(LeiPOIParser, self).parse_obj(row, operation)
        if not self.obj.pk:
            return
        geometry = self.obj.geom.transform(4326, clone=True)
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        topology = TopologyHelper.deserialize(serialized)
        # Move deserialization aggregations to the POI
        self.obj.mutate(topology)


class SitlorPOI(LeiPOIParser):
    url = "http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=233&pwkey=4dc5b1e31e5e8bf0d22810a9e5e8bbc8&urlnames=tous&PVALUES=4000012,29/09/2017 00:00:00,24/09/2018 23:59:59,MOSELLE,2,853000026,853000088|853000089&PNAMES=alcat,validaddu,validadau,elsector,utilisador,elcriterio0,modalidad0&lesvalid=|+12M&clause=233000281"
    label = u"SITLOR - POI : Site - Monument / Musée / Parc & Jardin"

    field_options = {
        'type': {
            'mapping': {
                '4000047': 'Inconnu',
                '4000048': 'Inconnu',
                '4000049': 'Inconnu',
            }
        }
    }

    def filter_description(self, src, val):
        (commentaire, contact, email, url) = val
        description = ""

        if commentaire:
            description = commentaire

        if contact:
            # delete duplicates
            contact = list(set(contact))
            description = '{}<br/><br/>Contact :'.format(description)

            for element in contact:
                if element:
                    description = '{}<br/>{}'.format(description, element)

        if email:
            # delete duplicates
            email = list(set(email))
            description = '{}<br/><br/>Email :'.format(description)
            for element in email:
                if element:
                    description = '{}<br/><a href="mailto:{}">{}</a>'.format(description, element, element)

        if url:
            # delete duplicates
            url = list(set(url))
            description = '{}<br/><br/>Site web :'.format(description)
            for element in url:
                if element:
                    if not element.startswith('http'):
                        element = 'http://' + element
                    description = '{}<br/><a href="{}">{}</a>'.format(description, element, element)

        return description


class LeiPOI(LeiPOIParser):
    url = "https://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000006_pnrvn_chateaux_musees.xml"
    label = u"LEI - POI : Musées et Châteaux-Forts"

    field_options = {
        'type': {
            'mapping': {
                '1900200': 'Inconnu',
            }
        }
    }

    def filter_description(self, src, val):
        (commentaire, contact, email, url) = val
        description = ""

        if commentaire:
            description = commentaire

        if contact:
            # delete duplicates
            contact = list(set(contact))
            description = '{}<br/><br/>Contact :'.format(description)

            for element in contact:
                if element:
                    description = '{}<br/>{}'.format(description, element)

        if email:
            # delete duplicates
            email = list(set(email))
            description = '{}<br/><br/>Email :'.format(description)
            for element in email:
                if element:
                    description = '{}<br/><a href="mailto:{}">{}</a>'.format(description, element, element)

        if url:
            # delete duplicates
            url = list(set(url))
            description = '{}<br/><br/>Site web :'.format(description)
            for element in url:
                if element:
                    if not element.startswith('http'):
                        element = 'http://' + element
                    description = '{}<br/><a href="{}">{}</a>'.format(description, element, element)

        return description