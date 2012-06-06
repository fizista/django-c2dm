# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MessageGroups.channel'
        db.delete_column('django_c2dm_messagegroups', 'channel_id')

        # Adding M2M table for field channel on 'MessageGroups'
        db.create_table('django_c2dm_messagegroups_channel', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('messagegroups', models.ForeignKey(orm['django_c2dm.messagegroups'], null=False)),
            ('messagechannels', models.ForeignKey(orm['django_c2dm.messagechannels'], null=False))
        ))
        db.create_unique('django_c2dm_messagegroups_channel', ['messagegroups_id', 'messagechannels_id'])


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'MessageGroups.channel'
        raise RuntimeError("Cannot reverse this migration. 'MessageGroups.channel' and its values cannot be restored.")
        # Removing M2M table for field channel on 'MessageGroups'
        db.delete_table('django_c2dm_messagegroups_channel')


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
            'Meta': {'ordering': "['name']", 'object_name': 'MessageGroups'},
            'channel': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.MessageChannels']", 'null': 'True', 'blank': 'True'}),
            'devices': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['django_c2dm.DeviceChannelInfo']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['django_c2dm']