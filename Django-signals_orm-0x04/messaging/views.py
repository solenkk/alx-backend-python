from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views import View
from django.utils.decorators import method_decorator
from .models import Message, Notification

@cache_page(60)
@login_required
def unread_messages(request):
    """
    View to display all unread messages for the current user
    with direct query optimization in the view
    """
    # Using the manager and adding additional optimization in the view
    unread_messages = Message.unread.unread_for_user(request.user).only(
        'id', 'content', 'timestamp', 'sender__username'
    )
    
    return render(request, 'messaging/unread_messages.html', {
        'unread_messages': unread_messages
    })
    ["sender=request.user"]

@require_POST
@login_required
def delete_user(request):
    """
    View to handle user account deletion with confirmation
    """
    user = request.user
    
    # Optional password confirmation for security
    if not user.check_password(request.POST.get('password', '')):
        messages.error(request, 'Incorrect password. Account not deleted.')
        return redirect('delete_confirmation')
    
    # Logout before deletion to prevent session issues
    from django.contrib.auth import logout
    logout(request)
    
    # Delete user account
    user.delete()
    
    messages.success(request, 'Your account has been permanently deleted.')
    return redirect('home')

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class MessageThreadView(View):
    """
    Class-based view for displaying message threads
    """
    def get(self, request, message_id):
        message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver', 'parent_message'),
            pk=message_id
        )
        thread_messages = Message.objects.filter(
            Q(pk=message_id) | Q(parent_message_id=message_id)
        ).select_related('sender', 'receiver')
        
        return render(request, 'messaging/thread.html', {
            'main_message': message,
            'thread_messages': thread_messages
        })

@login_required
def mark_as_read(request, message_id):
    """
    View to mark a message as read
    """
    message = get_object_or_404(
        Message.objects.filter(receiver=request.user),
        pk=message_id
    )
    if not message.read:
        message.read = True
        message.save()
    
    return redirect('message_detail', message_id=message_id)
