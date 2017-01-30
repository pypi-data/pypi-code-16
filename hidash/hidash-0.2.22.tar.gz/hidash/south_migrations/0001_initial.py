# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Chart'
        db.create_table(u'hidash_chart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('library', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('dimension', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('chart_type', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('query', self.gf('django.db.models.fields.TextField')(max_length=10000)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('grid_width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'hidash', ['Chart'])

        # Adding model 'ChartGroup'
        db.create_table(u'hidash_chartgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Chart'])),
        ))
        db.send_create_signal(u'hidash', ['ChartGroup'])

        # Adding model 'ChartMetric'
        db.create_table(u'hidash_chartmetric', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(related_name='chart', to=orm['hidash.Chart'])),
            ('metric', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'hidash', ['ChartMetric'])

        # Adding model 'ChartAuthGroup'
        db.create_table(u'hidash_chartauthgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Chart'])),
            ('auth_group', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hidash', ['ChartAuthGroup'])

        # Adding model 'ChartAuthPermission'
        db.create_table(u'hidash_chartauthpermission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.Chart'])),
            ('permission', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'hidash', ['ChartAuthPermission'])

        # Adding model 'ScheduledReport'
        db.create_table(u'hidash_scheduledreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'hidash', ['ScheduledReport'])

        # Adding M2M table for field report on 'ScheduledReport'
        m2m_table_name = db.shorten_name(u'hidash_scheduledreport_report')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scheduledreport', models.ForeignKey(orm[u'hidash.scheduledreport'], null=False)),
            ('chart', models.ForeignKey(orm[u'hidash.chart'], null=False))
        ))
        db.create_unique(m2m_table_name, ['scheduledreport_id', 'chart_id'])

        # Adding model 'ReportRecipients'
        db.create_table(u'hidash_reportrecipients', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_address', self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.ScheduledReport'])),
        ))
        db.send_create_signal(u'hidash', ['ReportRecipients'])

        # Adding model 'ScheduledReportParam'
        db.create_table(u'hidash_scheduledreportparam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter_name', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('parameter_value', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('scheduled_report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hidash.ScheduledReport'])),
        ))
        db.send_create_signal(u'hidash', ['ScheduledReportParam'])


    def backwards(self, orm):
        # Deleting model 'Chart'
        db.delete_table(u'hidash_chart')

        # Deleting model 'ChartGroup'
        db.delete_table(u'hidash_chartgroup')

        # Deleting model 'ChartMetric'
        db.delete_table(u'hidash_chartmetric')

        # Deleting model 'ChartAuthGroup'
        db.delete_table(u'hidash_chartauthgroup')

        # Deleting model 'ChartAuthPermission'
        db.delete_table(u'hidash_chartauthpermission')

        # Deleting model 'ScheduledReport'
        db.delete_table(u'hidash_scheduledreport')

        # Removing M2M table for field report on 'ScheduledReport'
        db.delete_table(db.shorten_name(u'hidash_scheduledreport_report'))

        # Deleting model 'ReportRecipients'
        db.delete_table(u'hidash_reportrecipients')

        # Deleting model 'ScheduledReportParam'
        db.delete_table(u'hidash_scheduledreportparam')


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
            'query': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'hidash.chartmetric': {
            'Meta': {'object_name': 'ChartMetric'},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chart'", 'to': u"orm['hidash.Chart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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