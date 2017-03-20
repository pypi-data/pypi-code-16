# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'hidash_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'hidash', ['Group'])

        # Adding model 'ChartGroup'
        db.create_table(u'hidash_chartgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Group'])),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Chart'])),
        ))
        db.send_create_signal(u'hidash', ['ChartGroup'])

        # Adding model 'ChartParameter'
        db.create_table(u'hidash_chartparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter_name', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('parameter_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('grid_width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Group'])),
        ))
        db.send_create_signal(u'hidash', ['ChartParameter'])

        # Adding field 'Chart.separator'
        db.add_column(u'hidash_chart', 'separator',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Group'
        db.delete_table(u'hidash_group')

        # Deleting model 'ChartGroup'
        db.delete_table(u'hidash_chartgroup')

        # Deleting model 'ChartParameter'
        db.delete_table(u'hidash_chartparameter')

        # Deleting field 'Chart.separator'
        db.delete_column(u'hidash_chart', 'separator')


    models = {
        u'hidash.chart': {
            'Meta': {'object_name': 'Chart'},
            'chart_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'dimension': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'grid_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {'max_length': '10000'}),
            'separator': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'hidash.chartauthgroup': {
            'Meta': {'object_name': 'ChartAuthGroup'},
            'auth_group': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.Chart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hidash.chartauthpermission': {
            'Meta': {'object_name': 'ChartAuthPermission'},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.Chart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'hidash.chartgroup': {
            'Meta': {'object_name': 'ChartGroup'},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.Chart']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hidash.chartmetric': {
            'Meta': {'object_name': 'ChartMetric'},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chart'", 'to': u"orm['hidash.Chart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'hidash.chartparameter': {
            'Meta': {'object_name': 'ChartParameter'},
            'grid_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'parameter_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hidash.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'hidash.reportrecipients': {
            'Meta': {'object_name': 'ReportRecipients'},
            'email_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.ScheduledReport']"})
        },
        u'hidash.scheduledreport': {
            'Meta': {'object_name': 'ScheduledReport'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hidash.Chart']", 'symmetrical': 'False'})
        },
        u'hidash.scheduledreportparam': {
            'Meta': {'object_name': 'ScheduledReportParam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'parameter_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'scheduled_report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.ScheduledReport']"})
        }
    }

    complete_apps = ['hidash']