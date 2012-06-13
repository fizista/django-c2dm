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
            ('registration_id', self.gf('django.db.models.fields.CharField')(default='', max_length=140, blank=True)),
            ('failed_push', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDevice'])

        # Adding model 'AndroidDeviceToken'
        db.create_table('django_c2dm_androiddevicetoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.AndroidDevice'])),
            ('registration_id', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('change_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=24, null=True, blank=True)),
            ('confirm', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDeviceToken'])

        # Adding model 'MessageData'
        db.create_table('django_c2dm_messagedata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.TextField')(max_length=950)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('django_c2dm', ['MessageData'])

        # Adding model 'MessageChannels'
        db.create_table('django_c2dm_messagechannels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('django_c2dm', ['MessageChannels'])

        # Adding M2M table for field message on 'MessageChannels'
        db.create_table('django_c2dm_messagechannels_message', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagechannels', models.ForeignKey(orm['django_c2dm.messagechannels'], null=False)),
            ('messagedata', models.ForeignKey(orm['django_c2dm.messagedata'], null=False))
        ))
        db.create_unique('django_c2dm_messagechannels_message', ['messagechannels_id', 'messagedata_id'])

        # Adding model 'MessageGroups'
        db.create_table('django_c2dm_messagegroups', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('django_c2dm', ['MessageGroups'])

        # Adding model 'DeviceChannelInfo'
        db.create_table('django_c2dm_devicechannelinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.AndroidDevice'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.MessageChannels'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.MessageGroups'])),
            ('last_message', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('django_c2dm', ['DeviceChannelInfo'])

        # Adding unique constraint on 'DeviceChannelInfo', fields ['device', 'channel', 'group']
        db.create_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id', 'group_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DeviceChannelInfo', fields ['device', 'channel', 'group']
        db.delete_unique('django_c2dm_devicechannelinfo', ['device_id', 'channel_id', 'group_id'])

        # Deleting model 'AndroidDevice'
        db.delete_table('django_c2dm_androiddevice')

        # Deleting model 'AndroidDeviceToken'
        db.delete_table('django_c2dm_androiddevicetoken')

        # Deleting model 'MessageData'
        db.delete_table('django_c2dm_messagedata')

        # Deleting model 'MessageChannels'
        db.delete_table('django_c2dm_messagechannels')

        # Removing M2M table for field message on 'MessageChannels'
        db.delete_table('django_c2dm_messagechannels_message')

        # Deleting model 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups')

        # Deleting model 'DeviceChannelInfo'
        db.delete_table('django_c2dm_devicechannelinfo')


    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '140', 'blank': 'True'})
        },
        'django_c2dm.androiddevicetoken': {
            'Meta': {'ordering': "['device', 'change_date']", 'object_name': 'AndroidDeviceToken'},
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'confirm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDevice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
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