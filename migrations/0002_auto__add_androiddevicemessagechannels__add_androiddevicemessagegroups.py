# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AndroidDeviceMessageChannels'
        db.create_table('django_c2dm_androiddevicemessagechannels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message', self.gf('django.db.models.fields.TextField')(max_length=950)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 5, 22, 0, 0), blank=True)),
        ))
        db.send_create_signal('django_c2dm', ['AndroidDeviceMessageChannels'])

        # Adding model 'AndroidDeviceMessageGroups'
        db.create_table('django_c2dm_androiddevicemessagegroups', (
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

        # Deleting field 'AndroidDevice.last_messaged'
        db.delete_column('django_c2dm_androiddevice', 'last_messaged')

        # Deleting field 'AndroidDevice.collapse_key'
        db.delete_column('django_c2dm_androiddevice', 'collapse_key')


    def backwards(self, orm):
        # Deleting model 'AndroidDeviceMessageChannels'
        db.delete_table('django_c2dm_androiddevicemessagechannels')

        # Deleting model 'AndroidDeviceMessageGroups'
        db.delete_table('django_c2dm_androiddevicemessagegroups')

        # Removing M2M table for field device on 'AndroidDeviceMessageGroups'
        db.delete_table('django_c2dm_androiddevicemessagegroups_device')

        # Adding field 'AndroidDevice.last_messaged'
        db.add_column('django_c2dm_androiddevice', 'last_messaged',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 5, 22, 0, 0), blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'AndroidDevice.collapse_key'
        raise RuntimeError("Cannot reverse this migration. 'AndroidDevice.collapse_key' and its values cannot be restored.")

    models = {
        'django_c2dm.androiddevice': {
            'Meta': {'object_name': 'AndroidDevice'},
            'device_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'failed_push': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_id': ('django.db.models.fields.CharField', [], {'max_length': '140'})
        },
        'django_c2dm.androiddevicemessagechannels': {
            'Meta': {'object_name': 'AndroidDeviceMessageChannels'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 22, 0, 0)', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'max_length': '950'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'django_c2dm.androiddevicemessagegroups': {
            'Meta': {'object_name': 'AndroidDeviceMessageGroups'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_c2dm.AndroidDeviceMessageChannels']"}),
            'device': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['django_c2dm.AndroidDevice']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['django_c2dm']