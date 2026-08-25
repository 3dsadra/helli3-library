from django import template
from web.models import User

register = template.Library()

@register.simple_tag
def create_user(username, password, is_admin=False):
    try:
        if User.objects.filter(username=username).exists():
            return f'Error: Username "{username}" already exists!'
        
        if isinstance(is_admin, str):
            is_admin = is_admin.lower() in ['on', 'true', '1', 'yes']
        else:
            is_admin = bool(is_admin)
        
        user = User(
            username=username,
            is_admin=is_admin,
        )
        user.set_password(password)
        user.save()
        
        role = "Admin" if is_admin else "Member"
        return f'Success: {role} "{username}" created successfully!'
    
    except Exception as e:
        return f'Error: {str(e)}'

@register.simple_tag
def delete_user(username):
    try:
        user = User.objects.get(username=username)
        user.delete()
        return f'Success: User "{username}" deleted successfully!'
    except User.DoesNotExist:
        return f'Error: User "{username}" not found!'

@register.simple_tag
def list_users():
    users = User.objects.all()
    if not users.exists():
        return "No users found."
    
    result = []
    for user in users:
        if user.is_admin:
            role = "👑 مدیر"
            role_class = "role-admin-badge"
        else:
            role = "📖 عضو"
            role_class = "role-member-badge"
        
        result.append(
            f'<div class="user-item">'
            f'<span class="user-username">{user.username}</span>'
            f'<span class="user-role-badge {role_class}">{role}</span>'
            f'</div>'
        )
    
    return "".join(result)

@register.simple_tag
def get_user(username):
    try:
        user = User.objects.get(username=username)
        if user.is_admin:
            role = "👑 مدیر"
            role_class = "role-admin-badge"
        else:
            role = "📖 عضو"
            role_class = "role-member-badge"
        
        return (
            f'<div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">'
            f'<p><strong>نام کاربری:</strong> {user.username}</p>'
            f'<p><strong>نقش:</strong> <span class="user-role-badge {role_class}">{role}</span></p>'
            f'<p><strong>شناسه:</strong> {user.id}</p>'
            f'</div>'
        )
    except User.DoesNotExist:
        return f'Error: User "{username}" not found!'

@register.simple_tag
def make_admin(username):
    try:
        user = User.objects.get(username=username)
        if user.is_admin:
            return f'Info: User "{username}" is already an admin!'
        user.is_admin = True
        user.save()
        return f'Success: User "{username}" is now an admin!'
    except User.DoesNotExist:
        return f'Error: User "{username}" not found!'

@register.simple_tag
def remove_admin(username):
    try:
        user = User.objects.get(username=username)
        if not user.is_admin:
            return f'Info: User "{username}" is not an admin!'
        user.is_admin = False
        user.save()
        return f'Success: Admin rights removed from "{username}"!'
    except User.DoesNotExist:
        return f'Error: User "{username}" not found!'