django-c2dm
=====

django-c2dm is a Django module for sending push messages to an Android device 
using Cloud 2 Device Messaging.  It provides a model to store the necessary information
required to send a message through C2DM as well as several helper functions.

## Setup

Using django-c2dm is easy.  Add the following line to your settings.py file: 

    C2DM_AUTH_USER = 'email'
    C2DM_AUTH_PASSWORD = 'password'
    C2DM_AUTH_ACCOUNT_TYPE = 'HOSTED or GOOGLE (default: GOOGLE)'
    C2DM_AUTH_APP_NAME = 'your app name'
    
or:

    C2DM_AUTH_TOKEN = 'YOUR_PUSH_ACCOUNT_AUTH_TOKEN'

Note: The token ClientLogin sometimes changes, so do not recommend this method.

Where YOUR_PUSH_ACCOUNT_AUTH_TOKEN is the ClientLogin token for your push account.

And then add django_c2dm and celery to your INSTALLED_APPS.

For urls.py file, add this code (or similar):

	url(r'^c2dm/', include('django_c2dm.urls', namespace='c2dm')),
	
If you need to log errors or exceptions, add to the file settings.py like this code:

	LOGGING['loggers']['django.c2dm'] = {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
             }

### Finding your ClientLogin token

You can retrieve the ClientLogin token for your push account via cURL:

    curl -X POST https://www.google.com/accounts/ClientLogin -d Email=ACCOUNT -d Passwd=PASSWORD -d accountType=HOSTED_OR_GOOGLE -d service=ac2dm

Just replace ACCOUNT and PASSWORD with the relevant information.

Copy everything in the response following Auth= to get your AUTH_TOKEN value.

## Usage

### Send mesage

To send a message to a device call send_message() on the model.  send_message() only needs kwargs as a parameter.
Use this to populate the data.X fields in your message.  These fields will be provided as extras on the intent
that the device receives.

You can also set the delay_while_idle parameter to True to enable this feature.

### Register device

Device registration on the site, in steps:

- application logs in to c2dm from google (receive registration_id)

- application sends to the server registration_id and device_id

         curl -X GET "http://<domain>/<path>/registration?device_id=<dev_id>&registration_id=<reg_id>"
         # if successful, returns the HTTP response code 200
     
- waiting for confirmation of registration by notification from the server c2dm.
  You get:
  
         data.registration_token = <token>
	 
- confirm receipt of registration information

         curl -X GET "http://<domain>/<path>/confirmation?device_id=<dev_id>&registration_token=<reg_token>"
         # if successful, returns the HTTP response code 200

Where:

- device_id - Unique ID for the device.  Simply used as a default method 
                to specify a device. For example: hash of a phone number, or/and
                or serial number. The ideal algorithm for this: sha256.
                The maximum length is 64 bytes, and minimum length is 8 bytes.

- registration_id - Result of calling registration intent on the device. 
                Subject to change.
                The maximum length is 140 bytes and minimum length is 8 bytes.
                
Errors:

- Http 400 - invalid data(for example: minimum, maximum, or lack device_id or registration_id or registration_token
- Http 500 - an application error
- Http 501 - attempt to queries by a method other than GET for example, POST




