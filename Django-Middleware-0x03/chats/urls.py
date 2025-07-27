from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Base router
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested messages router
conversation_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# Combine the routes
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]
