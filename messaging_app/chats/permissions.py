from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access or modify messages in that conversation.
    
    Rules:
    1. Only authenticated users can access the API
    2. For object-level permissions:
       - Read access (GET, HEAD, OPTIONS) allowed for participants
       - Write access (POST, PUT, PATCH, DELETE) allowed for participants
    """

    def has_permission(self, request, view):
        """
        Global permission check - allows access only to authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check - allows access only to conversation participants
        """
        # Check if user is a participant of the conversation
        is_participant = obj.conversation.participants.filter(id=request.user.id).exists()
        
        # For read-only methods, allow if participant
        if request.method in SAFE_METHODS:
            return is_participant
            
        # For write methods, also require participant status
        return is_participant
