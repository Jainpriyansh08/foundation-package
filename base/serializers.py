# noinspection PyMethodMayBeStatic
from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.utils import model_meta


class SerializerValidationCallbacksMixin:

    def before_validation(self, initial_data):  # pylint: disable-msg=R0201
        return initial_data

    def after_validation(self, validated_data):  # pylint: disable-msg=R0201
        return validated_data

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def is_valid(self, raise_exception=False):
        self.initial_data = self.before_validation(self.initial_data)
        return_data = super().is_valid(raise_exception)
        self._validated_data = self.after_validation(self.validated_data)
        return return_data


# noinspection PyUnresolvedReferences
class DynamicFieldsModelMixin:
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)

        if fields and exclude:
            raise AssertionError("Cannot pass both 'fields' and 'exclude' as an argument to {{class_name}}".format(
                class_name=self.__class__.__name__))

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name)


# noinspection PyAbstractClass
class ApplicationBaseSerializer(EnumSupportSerializerMixin, SerializerValidationCallbacksMixin, serializers.Serializer):
    pass


class ApplicationBaseModelSerializer(EnumSupportSerializerMixin, SerializerValidationCallbacksMixin,
                                     DynamicFieldsModelMixin, serializers.ModelSerializer):

    def apply_validated_data(self, validated_data):
        info = model_meta.get_field_info(self.instance)
        for attr, value in validated_data.items():
            if not (attr in info.relations and info.relations[attr].to_many):
                setattr(self.instance, attr, value)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if self.instance:
            for field in getattr(self, 'create_only_fields', []):
                data.pop(field)
        return data
