# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Email'
        db.create_table(u'db_email_backend_email', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('subject', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content_subtype', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('from_email', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
            ('to', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bcc', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('headers', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'db_email_backend', ['Email'])

        # Adding model 'EmailAlternative'
        db.create_table(u'db_email_backend_emailalternative', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'alternatives', to=orm['db_email_backend.Email'])),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
        ))
        db.send_create_signal(u'db_email_backend', ['EmailAlternative'])

        # Adding model 'EmailAttachment'
        db.create_table(u'db_email_backend_emailattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'attachments', to=orm['db_email_backend.Email'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=254, blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'db_email_backend', ['EmailAttachment'])


    def backwards(self, orm):
        # Deleting model 'Email'
        db.delete_table(u'db_email_backend_email')

        # Deleting model 'EmailAlternative'
        db.delete_table(u'db_email_backend_emailalternative')

        # Deleting model 'EmailAttachment'
        db.delete_table(u'db_email_backend_emailattachment')


    models = {
        u'db_email_backend.email': {
            'Meta': {'object_name': 'Email'},
            'bcc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_subtype': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'headers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'to': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'db_email_backend.emailalternative': {
            'Meta': {'object_name': 'EmailAlternative'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'alternatives'", 'to': u"orm['db_email_backend.Email']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'})
        },
        u'db_email_backend.emailattachment': {
            'Meta': {'object_name': 'EmailAttachment'},
            'email': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'attachments'", 'to': u"orm['db_email_backend.Email']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'})
        }
    }

    complete_apps = ['db_email_backend']