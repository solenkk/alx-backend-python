from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator

User = get_user_model()

class UserDeleteView(View):
    """Handles user account deletion with confirmation"""
    
    @method_decorator(login_required)
    def get(self, request):
        """Show confirmation page"""
        return render(request, 'messaging/confirm_delete.html')

    @method_decorator(login_required)
    def post(self, request):
        """Handle account deletion"""
        user = request.user
        
        # Optional: Add password confirmation for extra security
        password = request.POST.get('password', '')
        if not user.check_password(password):
            messages.error(request, 'Incorrect password. Account not deleted.')
            return redirect('delete_confirmation')
        
        # Logout before deletion to prevent session issues
        from django.contrib.auth import logout
        logout(request)
        
        # Delete user account
        user.delete()
        
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('home')

@require_http_methods(["GET", "POST"])
@login_required
def delete_user_legacy(request):
    """Alternative function-based view for account deletion"""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Account successfully deleted.')
        return redirect('home')
    return render(request, 'messaging/confirm_delete.html')
