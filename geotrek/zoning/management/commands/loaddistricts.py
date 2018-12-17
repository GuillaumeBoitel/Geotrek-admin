# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource, GDALException, OGRIndexError
from geotrek.zoning.models import District
from django.contrib.gis.geos.polygon import Polygon
from django.contrib.gis.geos.collections import MultiPolygon
from django.conf import settings


class Command(BaseCommand):
    help = 'Load Cities from a file within the spatial extent\n'

    def add_arguments(self, parser):
        parser.add_argument('districts', help="File's path of the districts")
        parser.add_argument('--name-attribute', '-n', action='store', dest='name', default='nom',
                            help="Name of the name's attribute inside the file")
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')
        parser.add_argument('--srid', '-s', action='store', dest='srid', default=4326,
                            help="File's SRID")
        parser.add_argument('--intersect', '-i', action='store_true', dest='intersect', default=False,
                            help="Check features intersect spatial extent and not only within")

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        file = options.get('districts')
        name_column = options.get('name')
        encoding = options.get('encoding')
        srid = options.get('srid')
        do_intersect = options.get('intersect')
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        ds = DataSource(file, encoding=encoding)
        count_error = 0

        for layer in ds:
            for feat in layer:
                try:
                    geom = feat.geom.geos
                    if not isinstance(geom, Polygon) and not isinstance(geom, MultiPolygon):
                        if verbosity > 0:
                            self.stdout.write("%s's geometry is not a polygon" % feat.get(name_column))
                        break
                    elif isinstance(geom, Polygon):
                        geom = MultiPolygon(geom)
                    self.check_srid(srid, geom)
                    geom.dim = 2
                    if do_intersect and bbox.intersects(geom) or not do_intersect and geom.within(bbox):
                        city, created = District.objects.update_or_create(name=feat.get(name_column),
                                                                          defaults={'geom': geom})
                        if verbosity > 0:
                            if created:
                                self.stdout.write("Created %s" % feat.get(name_column))
                            elif verbosity > 0:
                                self.stdout.write("Updated %s" % feat.get(name_column))
                except OGRIndexError:
                    if count_error == 0:
                        self.stdout.write(
                            "Name's attribute do not correspond with options\n"
                            "Please, use --name to fix it.\n"
                            "Fields in your file are : %s" % ', '.join(feat.fields))
                    count_error += 1
                except UnicodeEncodeError:
                    self.stdout.write("Problem of encoding with %s" % feat.get(name_column))

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = srid

        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                raise CommandError("SRID is not well configurate, change/add option srid")
