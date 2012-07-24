# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhysicalType'
        db.create_table('nature_sentier', (
            ('code', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column='code_physique')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='physique')),
        ))
        db.send_create_signal('land', ['PhysicalType'])

        # Adding model 'PhysicalEdge'
        db.create_table('nature', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('physical_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.PhysicalType'])),
        ))
        db.send_create_signal('land', ['PhysicalEdge'])

        # Adding model 'LandType'
        db.create_table('type_foncier', (
            ('code', self.gf('django.db.models.fields.AutoField')(primary_key=True, db_column='code_foncier')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='foncier')),
            ('right_of_way', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='droit_de_passage')),
        ))
        db.send_create_signal('land', ['LandType'])

        # Adding model 'LandEdge'
        db.create_table('foncier', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('land_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.LandType'])),
        ))
        db.send_create_signal('land', ['LandEdge'])

        # Adding model 'CompetenceEdge'
        db.create_table('competence', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Organism'])),
        ))
        db.send_create_signal('land', ['CompetenceEdge'])

        # Adding model 'WorkManagementEdge'
        db.create_table('gestion_travaux', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Organism'])),
        ))
        db.send_create_signal('land', ['WorkManagementEdge'])

        # Adding model 'SignageManagementEdge'
        db.create_table('gestion_signaletique', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Organism'])),
        ))
        db.send_create_signal('land', ['SignageManagementEdge'])

        # Adding model 'RestrictedArea'
        db.create_table('couche_zonage_reglementaire', (
            ('code', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='code_zonage')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='zonage')),
            ('order', self.gf('django.db.models.fields.IntegerField')(db_column='order')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['RestrictedArea'])

        # Adding model 'RestrictedAreaEdge'
        db.create_table('zonage', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('restricted_area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.RestrictedArea'])),
        ))
        db.send_create_signal('land', ['RestrictedAreaEdge'])

        # Adding model 'City'
        db.create_table('couche_communes', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True, db_column='insee')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='commune')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['City'])

        # Adding model 'CityEdge'
        db.create_table('commune', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.City'])),
        ))
        db.send_create_signal('land', ['CityEdge'])

        # Adding model 'District'
        db.create_table('couche_secteurs', (
            ('code', self.gf('django.db.models.fields.IntegerField')(primary_key=True, db_column='code_secteur')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='secteur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['District'])

        # Adding model 'DistrictEdge'
        db.create_table('secteur', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.TopologyMixin'], unique=True, primary_key=True, db_column='evenement')),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.District'])),
        ))
        db.send_create_signal('land', ['DistrictEdge'])


    def backwards(self, orm):
        # Deleting model 'PhysicalType'
        db.delete_table('nature_sentier')

        # Deleting model 'PhysicalEdge'
        db.delete_table('nature')

        # Deleting model 'LandType'
        db.delete_table('type_foncier')

        # Deleting model 'LandEdge'
        db.delete_table('foncier')

        # Deleting model 'CompetenceEdge'
        db.delete_table('competence')

        # Deleting model 'WorkManagementEdge'
        db.delete_table('gestion_travaux')

        # Deleting model 'SignageManagementEdge'
        db.delete_table('gestion_signaletique')

        # Deleting model 'RestrictedArea'
        db.delete_table('couche_zonage_reglementaire')

        # Deleting model 'RestrictedAreaEdge'
        db.delete_table('zonage')

        # Deleting model 'City'
        db.delete_table('couche_communes')

        # Deleting model 'CityEdge'
        db.delete_table('commune')

        # Deleting model 'District'
        db.delete_table('couche_secteurs')

        # Deleting model 'DistrictEdge'
        db.delete_table('secteur')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixin']", 'db_column': "'evenement'"})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interventions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.Intervention']", 'symmetrical': 'False'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixinKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'core.topologymixinkind': {
            'Meta': {'object_name': 'TopologyMixinKind', 'db_table': "'type_evenements'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'land.city': {
            'Meta': {'object_name': 'City', 'db_table': "'couche_communes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True', 'db_column': "'insee'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'commune'"})
        },
        'land.cityedge': {
            'Meta': {'object_name': 'CityEdge', 'db_table': "'commune'", '_ormbases': ['core.TopologyMixin']},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.City']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.competenceedge': {
            'Meta': {'object_name': 'CompetenceEdge', 'db_table': "'competence'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.district': {
            'Meta': {'object_name': 'District', 'db_table': "'couche_secteurs'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_secteur'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'secteur'"})
        },
        'land.districtedge': {
            'Meta': {'object_name': 'DistrictEdge', 'db_table': "'secteur'", '_ormbases': ['core.TopologyMixin']},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.District']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landedge': {
            'Meta': {'object_name': 'LandEdge', 'db_table': "'foncier'", '_ormbases': ['core.TopologyMixin']},
            'land_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.LandType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landtype': {
            'Meta': {'object_name': 'LandType', 'db_table': "'type_foncier'"},
            'code': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'code_foncier'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'foncier'"}),
            'right_of_way': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'droit_de_passage'"})
        },
        'land.physicaledge': {
            'Meta': {'object_name': 'PhysicalEdge', 'db_table': "'nature'", '_ormbases': ['core.TopologyMixin']},
            'physical_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.PhysicalType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.physicaltype': {
            'Meta': {'object_name': 'PhysicalType', 'db_table': "'nature_sentier'"},
            'code': ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'code_physique'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'physique'"})
        },
        'land.restrictedarea': {
            'Meta': {'object_name': 'RestrictedArea', 'db_table': "'couche_zonage_reglementaire'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_zonage'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'zonage'"}),
            'order': ('django.db.models.fields.IntegerField', [], {'db_column': "'order'"})
        },
        'land.restrictedareaedge': {
            'Meta': {'object_name': 'RestrictedAreaEdge', 'db_table': "'zonage'", '_ormbases': ['core.TopologyMixin']},
            'restricted_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.RestrictedArea']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.signagemanagementedge': {
            'Meta': {'object_name': 'SignageManagementEdge', 'db_table': "'gestion_signaletique'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.workmanagementedge': {
            'Meta': {'object_name': 'WorkManagementEdge', 'db_table': "'gestion_travaux'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'maintenance.contractor': {
            'Meta': {'object_name': 'Contractor', 'db_table': "'prestataires'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'interventions'"},
            'area': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disorders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'interventions'", 'symmetrical': 'False', 'to': "orm['maintenance.InterventionDisorder']"}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'heliport_cost': ('django.db.models.fields.FloatField', [], {}),
            'in_maintenance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'intervention_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.InterventionJob']", 'through': "orm['maintenance.ManDay']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'material_cost': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']", 'null': 'True', 'blank': 'True'}),
            'slope': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionStatus']"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {}),
            'typology': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionTypology']", 'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {})
        },
        'maintenance.interventiondisorder': {
            'Meta': {'object_name': 'InterventionDisorder', 'db_table': "'desordres'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'disorder_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'disorder_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'disorder_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionjob': {
            'Meta': {'object_name': 'InterventionJob', 'db_table': "'bib_fonctions'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionstatus': {
            'Meta': {'object_name': 'InterventionStatus', 'db_table': "'bib_de_suivi'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'status_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventiontypology': {
            'Meta': {'object_name': 'InterventionTypology', 'db_table': "'typologie_des_interventions'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'typology': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'typology_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'typology_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'typology_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'maintenance.manday': {
            'Meta': {'object_name': 'ManDay', 'db_table': "'journeeshomme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervention': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Intervention']"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionJob']"}),
            'nb_days': ('django.db.models.fields.IntegerField', [], {})
        },
        'maintenance.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'maintenance.project': {
            'Meta': {'object_name': 'Project', 'db_table': "'chantiers'"},
            'begin_year': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'constraint': ('django.db.models.fields.TextField', [], {}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['maintenance.Contractor']"}),
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {}),
            'founders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.Organism']", 'through': "orm['maintenance.Funding']", 'symmetrical': 'False'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'project_manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manage'", 'to': "orm['maintenance.Organism']"}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'own'", 'to': "orm['maintenance.Organism']"}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['land']
