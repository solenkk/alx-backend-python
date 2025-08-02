from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q, Index
from django.utils import timezone
from .managers import UnreadMessagesManager

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        related_name='sent_messages', 
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, 
        related_name='received_messages', 
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        related_name='edited_messages',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Last Edited By'
    )
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    # Managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom unread messages manager

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            Index(fields=['read']),
            Index(fields=['receiver', 'read']),
            Index(fields=['sender', 'receiver']),
            Index(fields=['parent_message']),
            Index(fields=['edited']),
        ]

    def __str__(self):
        return f"Message {self.id} from {self.sender} to {self.receiver}"

    @property
    def is_thread_start(self):
        return self.parent_message is None

class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message,
        related_name='history',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        related_name='message_edits',
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name_plural = "Message Histories"
        ordering = ['-edited_at']
        indexes = [
            Index(fields=['message']),
            Index(fields=['edited_at']),
        ]

    def __str__(self):
        return f"History for message {self.message.id} (saved at {self.edited_at})"

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            Index(fields=['user', 'read']),
            Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"
