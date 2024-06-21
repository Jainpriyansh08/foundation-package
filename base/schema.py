from rest_framework.schemas.openapi import SchemaGenerator


class BetterhalfAPISchemaGenerator(SchemaGenerator):

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema['info']['x-logo'] = {
            'url': 'https://gcpimages.betterhalf.ai/betterhalf_images/new-logo-animated.gif',
            'altText': 'Betterhalf logo',
        }
        return schema
