from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from .models import Message

# Function-based view example
@cache_page(60)  # Cache for 60 seconds
def message_list(request, conversation_id):
    messages = Message.objects.filter(
        conversation_id=conversation_id
    ).select_related('sender', 'receiver')
    return render(request, 'chats/message_list.html', {
        'messages': messages
    })

# Class-based view example (alternative)
@method_decorator(cache_page(60), name='dispatch')
class CachedMessageListView(View):
    def get(self, request, conversation_id):
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender', 'receiver').only(
            'id', 'content', 'timestamp', 'sender__username', 'receiver__username'
        )
        return render(request, 'chats/message_list.html', {
            'messages': messages
        })
