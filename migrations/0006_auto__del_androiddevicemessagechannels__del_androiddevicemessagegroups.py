# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AndroidDeviceMessageChannels'
        db.delete_table('django_c2dm_androiddevicemessagechannels')

        # Deleting model 'AndroidDeviceMessageGroups'
        db.delete_table('django_c2dm_androiddevicemessagegroups')

        # Removing M2M table for field device on 'AndroidDeviceMessageGroups'
        db.delete_table('django_c2dm_androiddevicemessagegroups_device')

        # Adding model 'MessageGroups'
        db.create_table('django_c2dm_messagegroups', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.MessageChannels'])),
        ))
        db.send_create_signal('django_c2dm', ['MessageGroups'])

        # Adding M2M table for field devices on 'MessageGroups'
        db.create_table('django_c2dm_messagegroups_devices', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagegroups', models.ForeignKey(orm['django_c2dm.messagegroups'], null=False)),
            ('devicechannelinfo', models.ForeignKey(orm['django_c2dm.devicechannelinfo'], null=False))
        ))
        db.create_unique('django_c2dm_messagegroups_devices', ['messagegroups_id', 'devicechannelinfo_id'])

        # Adding model 'MessageChannels'
        db.create_table('django_c2dm_messagechannels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('message', self.gf('django.db.models.fields.TextField')(max_length=950)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('django_c2dm', ['MessageChannels'])

        # Adding model 'DeviceChannelInfo'
        db.create_table('django_c2dm_devicechannelinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.AndroidDevice'])),
            ('last_message', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('django_c2dm', ['DeviceChannelInfo'])


    def backwards(self, orm):
        # Adding model 'AndroidDeviceMessageChannels'
        db.create_table('django_c2dm_androiddevicemessagechannels', (
            ('message', self.gf('django.db.models.fields.TextField')(max_length=950)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDeviceMessageChannels'])

        # Adding model 'AndroidDeviceMessageGroups'
        db.create_table('django_c2dm_androiddevicemessagegroups', (
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 5, 23, 0, 0), blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_c2dm.AndroidDeviceMessageChannels'])),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDeviceMessageGroups'])

        # Adding M2M table for field device on 'AndroidDeviceMessageGroups'
        db.create_table('django_c2dm_androiddevicemessagegroups_device', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('androiddevicemessagegroups', models.ForeignKey(orm['django_c2dm.androiddevicemessagegroups'], null=False)),
            ('androiddevice', models.ForeignKey(orm['django_c2dm.androiddevice'], null=False))
        ))
        db.create_unique('django_c2dm_androiddevicemessagegroups_device', ['androiddevicemessagegroups_id', 'androiddevice_id'])

        # Deleting model 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups')

        # Removing M2M table for field devices on 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups_devices')

        # Deleting model 'MessageChannels'
        db.delete_table('django_c2dm_messagechannels')

        # Deleting model 'DeviceChannelInfo'
        db.delete_table('django_c2dm_devicechannelinfo')


    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'ordering': "['device_id']", 'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'django_c2dm.devicechannelinfo': {
            'Meta': {'object_name': 'DeviceChannelInfo'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDevice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_message': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'django_c2dm.messagechannels': {
            'Meta': {'ordering': "['name']", 'object_name': 'MessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '950'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
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