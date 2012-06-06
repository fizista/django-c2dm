# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])

        # Removing M2M table for field devices on 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups_devices')

        # Removing M2M table for field channel on 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups_channel')

        # Adding field 'DeviceChannelInfo.group'
        db.add_column('django_c2dm_devicechannelinfo', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['django_c2dm.MessageGroups']),
                      keep_default=False)

        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'group', 'channel']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'group_id', 'channel_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'group', 'channel']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'group_id', 'channel_id'])

        # Adding M2M table for field devices on 'MessageGroups'
        db.create_table('django_c2dm_messagegroups_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagegroups', models.ForeignKey(orm['django_c2dm.messagegroups'], null=False)),
            ('devicechannelinfo', models.ForeignKey(orm['django_c2dm.devicechannelinfo'], null=False))
        ))
        db.create_unique('django_c2dm_messagegroups_devices', ['messagegroups_id', 'devicechannelinfo_id'])

        # Adding M2M table for field channel on 'MessageGroups'
        db.create_table('django_c2dm_messagegroups_channel', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagegroups', models.ForeignKey(orm['django_c2dm.messagegroups'], null=False)),
            ('messagechannels', models.ForeignKey(orm['django_c2dm.messagechannels'], null=False))
        ))
        db.create_unique('django_c2dm_messagegroups_channel', ['messagegroups_id', 'messagechannels_id'])

        # Deleting field 'DeviceChannelInfo.group'
        db.delete_column('django_c2dm_devicechannelinfo', 'group_id')

        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'channel']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id'])


    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'django_c2dm.devicechannelinfo': {
            'Meta': {'ordering': "['group', 'device', 'channel']", 'unique_together': "(('device', 'channel', 'group'),)", 'object_name': 'DeviceChannelInfo'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageChannels']"}),
            'device': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_c2dm.AndroidDevice']", 'unique': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.MessageGroups']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.DateTimeField', [], {}),
            'task': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagechannels': {
            'Meta': {'ordering': "['name']", 'object_name': 'MessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.MessageData']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'django_c2dm.messagedata': {
            'Meta': {'object_name': 'MessageData'},
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