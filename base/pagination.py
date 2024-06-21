from collections import OrderedDict

from django.utils import timezone
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param


class KeySetPagination(pagination.BasePagination):
    PRECISION = 1_000_000
    DEFAULT_LIMIT = api_settings.PAGE_SIZE
    DEFAULT_ORDER = 'DESC'
    LIMIT_QUERY_PARAM = 'limit'
    TIMESTAMP_QUERY_PARAM = 'timestamp'
    TIMESTAMP_MODEL_FIELD = 'created_at'
    next_page_available = False
    request = None
    limit = None
    last_element_timestamp = None

    def _get_limit(self, request):
        if self.LIMIT_QUERY_PARAM:
            try:
                return int(request.query_params[self.LIMIT_QUERY_PARAM])
            except (KeyError, ValueError):
                pass

        return self.DEFAULT_LIMIT

    def _get_timestamp(self, request):
        if self.TIMESTAMP_QUERY_PARAM:
            try:
                timestamp = int(request.query_params[self.TIMESTAMP_QUERY_PARAM])
                timestamp = float(timestamp) / self.PRECISION
                return timezone.datetime.fromtimestamp(timestamp, timezone.get_default_timezone())
            except (KeyError, ValueError):
                pass
        return None

    def _get_order_by(self):
        if self.DEFAULT_ORDER == 'ASC':
            return self.TIMESTAMP_MODEL_FIELD

        if self.DEFAULT_ORDER == 'DESC':
            return '-' + self.TIMESTAMP_MODEL_FIELD

        raise AssertionError('order must be either `ASC` or `DESC`')

    def _get_operator(self):
        if self.DEFAULT_ORDER == 'ASC':
            return 'gt'

        if self.DEFAULT_ORDER == 'DESC':
            return 'lt'

        raise AssertionError('order must be either `ASC` or `DESC`')

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.limit = self._get_limit(request)
        timestamp = self._get_timestamp(request)
        if timestamp:
            query = {f'{self.TIMESTAMP_MODEL_FIELD}__{self._get_operator()}': timestamp}
            queryset = queryset.filter(**query)

        paginated_queryset = self.get_paginated_queryset(queryset)
        if len(paginated_queryset) == self.limit + 1:
            paginated_queryset.pop()
            self.next_page_available = True
            self.last_element_timestamp = getattr(paginated_queryset[-1], self.TIMESTAMP_MODEL_FIELD).timestamp()
        return paginated_queryset

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('results', data)
        ]))

    def get_next_link(self):
        if not self.next_page_available:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.LIMIT_QUERY_PARAM, self.limit)

        new_timestamp = int(self.last_element_timestamp * self.PRECISION)
        return replace_query_param(url, self.TIMESTAMP_QUERY_PARAM, new_timestamp)

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'next': {
                    'type': 'string',
                    'format': 'url',
                    'nullable': True,
                    'example': 'http://api.staging.betterhalf.ai/example/?after=1585748268846043&limit=100'
                },
                'results': schema,
            },
        }

    def to_html(self):
        pass

    def get_paginated_queryset(self, queryset):
        return list(queryset.order_by(self._get_order_by())[:self.limit + 1])


class BeforeLimitPaginationWithGenericSortField(KeySetPagination):
    TIMESTAMP_QUERY_PARAM = 'before'

    def get_paginated_queryset(self, queryset):
        return list(queryset[:self.limit + 1])


class BeforeLimitPagination(KeySetPagination):
    TIMESTAMP_QUERY_PARAM = 'before'
