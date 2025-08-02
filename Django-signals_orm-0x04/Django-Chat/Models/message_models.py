from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

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

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

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

    def __str__(self):
        return f"History for message {self.message.id}"
    from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q
from django.utils import timezone

User = get_user_model()

class MessageManager(models.Manager):
    def get_conversation_threads(self, user):
        """
        Get all conversation threads for a user with optimized queries
        """
        return self.filter(
            Q(sender=user) | Q(receiver=user),
            parent_message__isnull=True  # Only top-level messages
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            Prefetch('replies',
                queryset=Message.objects.select_related('sender', 'receiver')
                    .prefetch_related('replies')
                    .order_by('timestamp'),
                to_attr='threaded_replies'
            )
        ).order_by('-timestamp')

    def get_full_thread(self, message_id):
        """
        Get a complete message thread with all nested replies
        """
        return self.filter(
            Q(pk=message_id) | Q(parent_message_id=message_id)
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).order_by('timestamp')

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
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE,
        verbose_name='Parent Message'
    )
    read = models.BooleanField(default=False)

    objects = MessageManager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['parent_message']),
            models.Index(fields=['sender', 'receiver']),
        ]

    def __str__(self):
        return f"Message {self.id} from {self.sender} to {self.receiver}"

    @property
    def is_thread_start(self):
        return self.parent_message is None

    def get_thread(self):
        """
        Recursive method to get all nested replies
        """
        def build_thread(message):
            thread = {
                'message': message,
                'replies': []
            }
            for reply in message.replies.all().select_related('sender', 'receiver'):
                thread['replies'].append(build_thread(reply))
            return thread

        return build_thread(self)
