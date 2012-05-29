# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'AndroidDeviceMessageChannels', fields ['name']
        db.create_unique('django_c2dm_androiddevicemessagechannels', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'AndroidDeviceMessageChannels', fields ['name']
        db.delete_unique('django_c2dm_androiddevicemessagechannels', ['name'])


    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'django_c2dm.androiddevicemessagechannels': {
            'Meta': {'ordering': "['name']", 'object_name': 'AndroidDeviceMessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '950'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'django_c2dm.androiddevicemessagegroups': {
            'Meta': {'ordering': "['channel']", 'object_name': 'AndroidDeviceMessageGroups'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDeviceMessageChannels']"}),
            'device': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_c2dm.AndroidDevice']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 23, 0, 0)', 'blank': 'True'})
        }
    }

    complete_apps = ['django_c2dm']