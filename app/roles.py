from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

CLIENT_GROUP = 'Клиент'
MANAGER_GROUP = 'Менеджер'


def _in_group(user, name):
    if not user.is_authenticated:
        return False
    groups = getattr(user, '_role_groups', None)
    if groups is None:
        groups = set(user.groups.values_list('name', flat=True))
        user._role_groups = groups
    return name in groups


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def is_manager(user):
    return not is_admin(user) and _in_group(user, MANAGER_GROUP)


def is_client(user):
    return (user.is_authenticated and not user.is_superuser
            and not _in_group(user, MANAGER_GROUP)
            and _in_group(user, CLIENT_GROUP))


def role_required(check):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not check(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator