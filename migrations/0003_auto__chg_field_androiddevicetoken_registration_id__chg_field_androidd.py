# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AndroidDeviceToken.registration_id'
        db.alter_column('django_c2dm_androiddevicetoken', 'registration_id', self.gf('django.db.models.fields.CharField')(max_length=5000))

        # Changing field 'AndroidDevice.registration_id'
        db.alter_column('django_c2dm_androiddevice', 'registration_id', self.gf('django.db.models.fields.CharField')(max_length=5000))

    def backwards(self, orm):

        # Changing field 'AndroidDeviceToken.registration_id'
        db.alter_column('django_c2dm_androiddevicetoken', 'registration_id', self.gf('django.db.models.fields.CharField')(max_length=180))

        # Changing field 'AndroidDevice.registration_id'
        db.alter_column('django_c2dm_androiddevice', 'registration_id', self.gf('django.db.models.fields.CharField')(max_length=180))

    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5000', 'blank': 'True'})
        },
        'django_c2dm.androiddevicetoken': {
            'Meta': {'ordering': "['device', 'change_date']", 'object_name': 'AndroidDeviceToken'},
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDevice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'})
        },
        'django_c2dm.devicechannelinfo': {
            'Meta': {'ordering': "['group', 'device', 'channel']", 'unique_together': "(('device', 'channel', 'group'),)", 'object_name': 'DeviceChannelInfo'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageChannels']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDevice']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageGroups']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'task': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagechannels': {
            'Meta': {'ordering': "['name']", 'object_name': 'MessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.MessageData']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'django_c2dm.messagedata': {
            'Meta': {'ordering': "['name']", 'object_name': 'MessageData'},
            'data': ('django.db.models.fields.TextField', [], {'max_length': '950'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagegroups': {
            'Meta': {'object_name': 'MessageGroups'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['django_c2dm']