# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

# Include the router URLs
urlpatterns = [
    path('', include(router.urls)),  # This line includes all the routes from the router
]
["routers.DefaultRouter()"]
