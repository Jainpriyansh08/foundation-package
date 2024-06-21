import json

from django_fsm import FSMFieldMixin
from enumfields import EnumField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ImageField, FileField

from base.mixins.aws import AWSFileFieldMixin


class AWSImageField(AWSFileFieldMixin, ImageField):
    pass


class AWSFileField(AWSFileFieldMixin, FileField):
    pass


class FSMEnumField(FSMFieldMixin, EnumField):
    pass


class PhoneNumberField(serializers.CharField):
    def __init__(self, **kwargs):
        self._kwargs['max_length'] = kwargs.get('max_length') or 15
        self._kwargs['min_length'] = kwargs.get('min_length') or 4
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not value.isnumeric():
            raise ValidationError("Mobile number must be numeric.")

        return value


class IsdCodeField(serializers.CharField):

    def __init__(self, **kwargs):
        self._kwargs['max_length'] = 5
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value.startswith('+'):
            value = value[1:]
        if not value.isnumeric():
            raise ValidationError("ISD code should be a numeric string which can optionally start with +")

        return value


class TrueCallerPhoneNumberField(IsdCodeField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kwargs['max_length'] = 15


class JsonFileReaderField(serializers.Field):

    def __init__(self, **kwargs):
        self.file_path = kwargs.pop('file_path')
        self.key_name = None
        if 'key_name' in kwargs:
            self.key_name = kwargs.pop('key_name')
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        try:
            with open(self.file_path) as file:
                file_json_data = json.load(file)
                if self.key_name is None:
                    return file_json_data
                return file_json_data.get(self.key_name, None)
        except FileNotFoundError:
            raise FileNotFoundError()
