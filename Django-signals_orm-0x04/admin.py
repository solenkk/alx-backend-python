from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'read', 'edited')
    list_filter = ('read', 'edited', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')
    raw_id_fields = ('sender', 'receiver', 'parent_message')
    date_hierarchy = 'timestamp'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    raw_id_fields = ('user', 'message')
    date_hierarchy = 'created_at'

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'edited_at')
    raw_id_fields = ('message',)
    date_hierarchy = 'edited_at'
    readonly_fields = ('edited_at',)
