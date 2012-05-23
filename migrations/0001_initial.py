# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AndroidDevice'
        db.create_table('django_c2dm_androiddevice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('registration_id', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('collapse_key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_messaged', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 5, 22, 0, 0), blank=True)),
            ('failed_push', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDevice'])


    def backwards(self, orm):
        # Deleting model 'AndroidDevice'
        db.delete_table('django_c2dm_androiddevice')


    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'object_name': 'AndroidDevice'},
            'collapse_key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_messaged': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 22, 0, 0)', 'blank': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        }
    }

    complete_apps = ['django_c2dm']