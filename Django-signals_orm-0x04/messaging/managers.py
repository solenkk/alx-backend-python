from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Returns unread messages for a specific user
        Optimized to only fetch necessary fields
        """
        return self.get_queryset().filter(
            receiver=user,
            read=False
        ).select_related(
            'sender'
        ).only(
            'id', 'content', 'timestamp', 'sender__username', 'sender__id'
        )
