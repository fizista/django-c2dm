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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import get_current_timezone, get_default_timezone

from .models import AndroidDevice, MessageChannels, MessageGroups, \
                    DeviceChannelInfo, MessageData

def registration_id(object):
    max_len = 24
    postfix = ' ...'
    if len(object.registration_id) > max_len:
        return '%s%s' % (object.registration_id[:(max_len - len(postfix))],
                         postfix)
    else:
        return object.registration_id
registration_id.short_description = _('Registration ID')


class AndroidDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'device_id',
        registration_id,
        'failed_push'
    )


class MessageDataAdmin(admin.ModelAdmin):
    list_display = (
        'key_name',
        'last_change'
    )


def last_change_info(object):
    return object._get_last_change().astimezone(get_current_timezone())
last_change_info.short_description = _('Last change')


class MessageChannelsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        last_change_info,
        'collapse_key'
    )


class DeviceChannelInfoInlineAdmin(admin.TabularInline):
    model = DeviceChannelInfo
    fk_name = 'group'
    verbose_name = _('List devices')
    verbose_name_plural = _('List devices')
    readonly_fields = ('device', 'channel', 'group', 'last_message', 'task')
    ordering = ('device',)


class MessageGroupsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    inlines = [
        DeviceChannelInfoInlineAdmin,
    ]
#    fieldsets = (
#        (None, {
#            'fields': ('name',)
#        }),
#        (_('Advanced options'), {
#            'classes': ('collapse',),
#            'fields': ('enable_comments', 'registration_required', 'template_name')
#        }),
#    )


class DeviceChannelInfoAdmin(admin.ModelAdmin):
    list_display = (
        'device',
        'channel',
        'last_message'
    )

admin.site.register(DeviceChannelInfo, DeviceChannelInfoAdmin)
admin.site.register(MessageData, MessageDataAdmin)
admin.site.register(MessageChannels, MessageChannelsAdmin)
admin.site.register(MessageGroups, MessageGroupsAdmin)
admin.site.register(AndroidDevice, AndroidDeviceAdmin)
