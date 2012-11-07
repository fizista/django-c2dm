# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'group', 'channel']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'group_id', 'channel_id'])

        # Deleting field 'DeviceChannelInfo.group'
        db.delete_column('django_c2dm_devicechannelinfo', 'group_id')

        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])

        # Adding M2M table for field devices on 'MessageGroups'
        db.create_table('django_c2dm_messagegroups_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagegroups', models.ForeignKey(orm['django_c2dm.messagegroups'], null=False)),
            ('androiddevice', models.ForeignKey(orm['django_c2dm.androiddevice'], null=False))
        ))
        db.create_unique('django_c2dm_messagegroups_devices', ['messagegroups_id', 'androiddevice_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])


        # User chose to not deal with backwards NULL issues for 'DeviceChannelInfo.group'
        raise RuntimeError("Cannot reverse this migration. 'DeviceChannelInfo.group' and its values cannot be restored.")
        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'group', 'channel']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'group_id', 'channel_id'])

        # Removing M2M table for field devices on 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups_devices')


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
            'Meta': {'ordering': "['device', 'channel']", 'unique_together': "(('device', 'channel'),)", 'object_name': 'DeviceChannelInfo'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageChannels']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDevice']"}),
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
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_c2dm.AndroidDevice']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['django_c2dm']