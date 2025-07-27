import django_filters
from .models import Message
from django.db.models import Q

class MessageFilter(django_filters.FilterSet):
    conversation_id = django_filters.NumberFilter(field_name='conversation__id')
    sender_id = django_filters.NumberFilter(field_name='sender__id')
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Message
        fields = ['conversation_id', 'sender_id', 'start_date', 'end_date', 'search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(message_body__icontains=value) |
            Q(sender__username__icontains=value)
        )
