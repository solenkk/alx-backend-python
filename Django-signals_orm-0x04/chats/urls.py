from django.urls import path
from .views import message_list, CachedMessageListView

urlpatterns = [
    # Function-based view URL
    path('conversation/<int:conversation_id>/', message_list, name='message_list'),
    
    # OR Class-based view URL
    path('conversation-cbv/<int:conversation_id>/', CachedMessageListView.as_view(), name='cached_message_list'),
]
