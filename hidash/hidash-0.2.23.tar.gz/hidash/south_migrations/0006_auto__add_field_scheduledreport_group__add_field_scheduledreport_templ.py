# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ScheduledReport.group'
        db.add_column(u'hidash_scheduledreport', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['hidash.Group']),
                      keep_default=False)

        # Adding field 'ScheduledReport.template'
        db.add_column(u'hidash_scheduledreport', 'template',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field report on 'ScheduledReport'
        db.delete_table(db.shorten_name(u'hidash_scheduledreport_report'))


    def backwards(self, orm):
        # Deleting field 'ScheduledReport.group'
        db.delete_column(u'hidash_scheduledreport', 'group_id')

        # Deleting field 'ScheduledReport.template'
        db.delete_column(u'hidash_scheduledreport', 'template')

        # Adding M2M table for field report on 'ScheduledReport'
        m2m_table_name = db.shorten_name(u'hidash_scheduledreport_report')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scheduledreport', models.ForeignKey(orm[u'hidash.scheduledreport'], null=False)),
            ('chart', models.ForeignKey(orm[u'hidash.chart'], null=False))
        ))
        db.create_unique(m2m_table_name, ['scheduledreport_id', 'chart_id'])


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
            'cron_expression': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['hidash.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_run_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_run_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'hidash.scheduledreportparam': {
            'Meta': {'object_name': 'ScheduledReportParam'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_parameter_value_sql_function': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parameter_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'parameter_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'scheduled_report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hidash.ScheduledReport']"})
        }
    }

    complete_apps = ['hidash']