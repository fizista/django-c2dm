# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MessageData'
        db.create_table('django_c2dm_messagedata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=950)),
        ))
        db.send_create_signal('django_c2dm', ['MessageData'])

        # Deleting field 'MessageChannels.message'
        db.delete_column('django_c2dm_messagechannels', 'message')

        # Adding M2M table for field message on 'MessageChannels'
        db.create_table('django_c2dm_messagechannels_message', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagechannels', models.ForeignKey(orm['django_c2dm.messagechannels'], null=False)),
            ('messagedata', models.ForeignKey(orm['django_c2dm.messagedata'], null=False))
        ))
        db.create_unique('django_c2dm_messagechannels_message', ['messagechannels_id', 'messagedata_id'])


    def backwards(self, orm):
        # Deleting model 'MessageData'
        db.delete_table('django_c2dm_messagedata')


        # User chose to not deal with backwards NULL issues for 'MessageChannels.message'
        raise RuntimeError("Cannot reverse this migration. 'MessageChannels.message' and its values cannot be restored.")
        # Removing M2M table for field message on 'MessageChannels'
        db.delete_table('django_c2dm_messagechannels_message')


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
            'message': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.MessageData']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'django_c2dm.messagedata': {
            'Meta': {'object_name': 'MessageData'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '950'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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