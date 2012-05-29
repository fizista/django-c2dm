# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DeviceChannelInfo.device'
        db.add_column('django_c2dm_devicechannelinfo', 'device',
                      self.gf('django.db.models.fields.related.OneToOneField')(null=True, to=orm['django_c2dm.AndroidDevice'], unique=True),
                      keep_default=False)


        # Changing field 'DeviceChannelInfo.channel'
        db.alter_column('django_c2dm_devicechannelinfo', 'channel_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.MessageChannels']))
        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])

        # Deleting field 'DeviceChannelInfo.device'
        db.delete_column('django_c2dm_devicechannelinfo', 'device_id')


        # Changing field 'DeviceChannelInfo.channel'
        db.alter_column('django_c2dm_devicechannelinfo', 'channel_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.AndroidDevice']))

    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'django_c2dm.devicechannelinfo': {
            'Meta': {'ordering': "['device', 'channel']", 'unique_together': "(('device', 'channel'),)", 'object_name': 'DeviceChannelInfo'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageChannels']"}),
            'device': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_c2dm.AndroidDevice']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagechannels': {
            'Meta': {'ordering': "['name']", 'object_name': 'MessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.MessageData']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'django_c2dm.messagedata': {
            'Meta': {'object_name': 'MessageData'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '950'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagegroups': {
            'Meta': {'ordering': "['channel']", 'object_name': 'MessageGroups'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageChannels']"}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_c2dm.DeviceChannelInfo']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['django_c2dm']
