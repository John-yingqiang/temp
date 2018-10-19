from django import forms
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator, _lazy_re_compile
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from distutils.version import StrictVersion


class ObjectIdField(serializers.CharField):

    def __init__(self, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = False
        self.max_length = 24
        self.min_length = 24
        super(serializers.CharField, self).__init__(**kwargs)
        message = self.error_messages['max_length'].format(max_length=self.max_length)
        self.validators.append(MaxLengthValidator(self.max_length, message=message))
        message = self.error_messages['min_length'].format(min_length=self.min_length)
        self.validators.append(MinLengthValidator(self.min_length, message=message))
        self.validators.append(RegexValidator(
            _lazy_re_compile('^[\da-f]+$'),
            message=_('Enter a valid id.'),
            code='invalid',))


class ReletiveUrlFormField(forms.CharField):
    default_validators = []


class RelativeUrlField(models.URLField):
    default_validators = []

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        defaults = {
            'form_class': ReletiveUrlFormField,
        }
        defaults.update(kwargs)
        return super(RelativeUrlField, self).formfield(**defaults)


class StrictVersionField(serializers.CharField):

    def to_internal_value(self, data):
        try:
            return StrictVersion(data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
