# -*-*- encoding: utf-8 -*-*-

import sys
import json
import datetime
import uuid
import hashlib
import urllib2

from flask.ext.wtf import TextField, PasswordField, Required, URL, ValidationError

from labmanager.forms import AddForm
from labmanager.rlms import register, Laboratory, Capabilities
from labmanager.rlms.base import BaseRLMS, BaseFormCreator, Versions

class QuVisAddForm(AddForm):

    DEFAULT_URL = 'http://www.st-andrews.ac.uk/physics/quvis/'
    DEFAULT_LOCATION = 'St Andrews (ScotLand)'
    DEFAULT_PUBLICLY_AVAILABLE = True
    DEFAULT_PUBLIC_IDENTIFIER = 'quvis'
    DEFAULT_AUTOLOAD = True

    def __init__(self, add_or_edit, *args, **kwargs):
        super(QuVisAddForm, self).__init__(*args, **kwargs)
        self.add_or_edit = add_or_edit

    @staticmethod
    def process_configuration(old_configuration, new_configuration):
        return new_configuration

class QuVisFormCreator(BaseFormCreator):

    def get_add_form(self):
        return QuVisAddForm

FORM_CREATOR = QuVisFormCreator()

# URLs:
# http://www.st-andrews.ac.uk/physics/quvis/simulations_twolev/
# http://www.st-andrews.ac.uk/physics/quvis/simulations_html5/sims/

class RLMS(BaseRLMS):

    def __init__(self, configuration):
        pass

    def get_version(self):
        return Versions.VERSION_1

    def get_capabilities(self):
        return [] 

    def get_laboratories(self):
        return [ 
            Laboratory('foo', 'bar', autoload = True) 
        ]

    def reserve(self, laboratory_id, username, institution, general_configuration_str, particular_configurations, request_payload, user_properties, *args, **kwargs):


        return {
            'reservation_id' : url,
            'load_url' : url
        }

register("QuVis", ['1.0'], __name__)

