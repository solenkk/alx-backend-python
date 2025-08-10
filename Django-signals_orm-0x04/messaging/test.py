from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, track_message_edits

User = get_user_model()

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )

    def test_message_creation(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        self.assertEqual(msg.sender, self.user1)
        self.assertEqual(msg.receiver, self.user2)
        self.assertFalse(msg.read)
        self.assertFalse(msg.edited)

    def test_notification_signal(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        notification = Notification.objects.get(message=msg)
        self.assertEqual(notification.user, self.user2)

    def test_message_edit_history(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        msg.content = "Edited content"
        msg.save()
        
        history = MessageHistory.objects.get(message=msg)
        self.assertEqual(history.content, "Original content")
        self.assertTrue(msg.edited)

    def test_unread_manager(self):
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message"
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            read=True
        )
        
        unread_count = Message.unread.for_user(self.user2).count()
        self.assertEqual(unread_count, 1)

    def test_user_deletion_cascade(self):
        msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test cascade"
        )
        self.user2.delete()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=msg.pk)
