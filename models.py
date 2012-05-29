# Copyright (c) 2010, Scott Ferguson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the software nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY SCOTT FERGUSON ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL SCOTT FERGUSON BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import hashlib
import urllib, urllib2
from urllib2 import URLError

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

C2DM_URL = 'https://android.apis.google.com/c2dm/send'
MAX_MESSAGE_SIZE = 1024


class AndroidDeviceException(Exception):
    pass


class AndroidDevice(models.Model):
    '''
    Profile of a c2dm-enabled Android device

    device_id - Unique ID for the device.  Simply used as a default method 
                to specify a device. For example: hash of a phone number, or
                or serial number. The ideal algorithm for this: sha256
    registration_id - Result of calling registration intent on the device. 
                Subject to change.
    collapse_key - Required arbitrary collapse_key string.
    last_messaged - When did we last send a push to the device
    failed_push - Have we had a failure when pushing to this device? Flag it here.
    '''
    device_id = models.CharField(max_length=64, unique=True) # hash of a phone 
                                                             # number, or serial 
                                                             # number. The best use for this sha256
    registration_id = models.CharField(max_length=140)
    failed_push = models.BooleanField(default=False)

    class Meta:
        ordering = ['device_id']
        verbose_name = _(u'android device')
        verbose_name_plural = _(u'android devices')

    def send_message(self, delay_while_idle=False, **kwargs):
        '''
        Sends a message to the device.  
        
        delay_while_idle - If included, indicates that the message should not be sent immediately if the device is idle. The server will wait for the device to become active, and then only the last message for each collapse_key value will be sent.
        data.keyX fields are populated via kwargs.
        '''
        if self.failed_push:
            return

        values = {
            'registration_id': self.registration_id,
            'collapse_key': self.collapse_key,
        }

        if delay_while_idle:
            values['delay_while_idle'] = ''

        for key, value in kwargs.items():
            values['data.%s' % key] = value

        headers = {
            'Authorization': 'GoogleLogin auth=%s' % settings.C2DM_AUTH_TOKEN,
        }

        try:
            params = urllib.urlencode(values)
            request = urllib2.Request(C2DM_URL, params, headers)

            # Make the request
            response = urllib2.urlopen(request)

            result = response.read().split('=')

            if 'Error' in result:
                if result[1] == 'InvalidRegistration' or result[1] == 'NotRegistered':
                    self.failed_push = True
                    self.save()

                raise AndroidDeviceException(result[1])
        except URLError, error:
            import logging
            logger = logging.getLogger('django_c2dm')
            logger.error('URLError: %s' % (error,))
            return False
        except AndroidDeviceException, error:
            import logging
            logger = logging.getLogger('django_c2dm')
            logger.info('AndroidDeviceException: %s' % (error,))
            return False
        except Exception, error:
            import logging
            logger = logging.getLogger('django_c2dm')
            logger.error('Exception: %s' % (error,))
            return False

    def __unicode__(self):
        return '%s' % self.device_id


class MessageData(models.Model):
    '''
    Message data
    
    last_change - last change data in the channel
    '''
    name = models.CharField(max_length=50, blank=True, null=True,
                                                   verbose_name=_(u'name'))
    data = models.TextField(max_length=950, verbose_name=_(u'data'))
    last_change = models.DateTimeField(auto_now=True,
                                                verbose_name=_(u'last change'))

    def key_name(self):
        'Return key name'
        return self.name or hex(self.id)[2:]
    key_name.short_description = 'Key name X'

    def __unicode__(self):
        return '%s' % (self.key_name())


class MessageChannels(models.Model):
    '''
    Message channels
    
    name - name of the channel
    message - message data
    last_change - last change data in the channel
    
    collapse_key - The key channel automatically generated based on the name 
                   and id of the channel.
    '''
    name = models.CharField(max_length=50, unique=True,
                                                       verbose_name=_(u'name'))
    message = models.ManyToManyField(MessageData, blank=True, null=True,
                                               verbose_name=_(u'message data'))


    class Meta:
        ordering = ['name']
        verbose_name = _(u'message channel')
        verbose_name_plural = _(u'message channels')

    def _get_collapse_key(self):
        'Return collapse_key (size 32 bytes)'
        return hashlib.md5(str(self.name) + str(self.id)).hexdigest()
    collapse_key = property(_get_collapse_key)

    def _get_last_change(self):
        'Return last change data in the channel'
        #self.message.
        return hashlib.md5(str(self.name) + str(self.id)).hexdigest()
    last_change = property(_get_last_change)

    def clean(self):
        from django.core.exceptions import ValidationError
        from urllib2 import quote
        from django.utils.encoding import smart_str

        def size(text_unicode):
            return len(quote(smart_str(text_unicode, "utf8")))

        # Calculate message size
        message_size = 0
        numeric_keys = 0
        for md in self.message.all():
            message_size += size(md.key_name)
            # Size data
            message_size += size(md.data)
        # Size collapse_key
        message_size += size(self.collapse_key)

        if MAX_MESSAGE_SIZE < message_size:
            raise ValidationError(('The maximum message size is %d,' + \
                                  ' but the message size is %d') %
                                  (MAX_DATA_SIZE, message_size))

    def save(self, *args, **kwargs):
        super(MessageChannels, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.name


class DeviceChannelInfo(models.Model):
    '''
    Device channel info
    
    last_message - When did we last send a push to the device
    '''
    device = models.OneToOneField(AndroidDevice)
    channel = models.ForeignKey(MessageChannels)
    last_message = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('device', 'channel'),)
        ordering = ['device', 'channel']
        verbose_name = _(u'Device channel info')
        verbose_name_plural = _(u'Device channel info')

    def __unicode__(self):
        return '%s-%s' % (self.device, self.channel.name)


class MessageGroups(models.Model):
    '''
    Message groups
    
    name - name of the group
    channel - channel type
    devices - list of devices
    '''
    name = models.CharField(max_length=50, unique=True,
                                                       verbose_name=_(u'name'))
    channel = models.ForeignKey(MessageChannels)
    devices = models.ManyToManyField(DeviceChannelInfo)

    class Meta:
        ordering = ['channel']
        verbose_name = _(u'message group')
        verbose_name_plural = _(u'message groups')

    def __unicode__(self):
        return '%s' % self.channel.name



def send_multiple_messages(device_list, **kwargs):
    '''
    Same as send_message but sends to a list of devices.

    data.keyX fields are populated via kwargs.
    '''
    for device in device_list:
        device.send_message(kwargs)

def filter_failed_devices():
    '''
    Removes any devices with failed registration_id's from the database
    '''
    for device in AndroidDevice.objects.filter(failed_push=True):
        device.delete()

def registration_completed_callback(sender, **kwargs):
    '''
    Returns a push response when the device has successfully registered.
    '''
    profile = kwargs['instance']
    profile.send_message(message='Registration successful', result='1')
#post_save.connect(registration_completed_callback, sender=AndroidDevice)


