from .roles import is_admin, is_manager, is_client


def roles(request):
    user = request.user
    return {
        'is_admin': is_admin(user),
        'is_manager': is_manager(user),
        'is_client': is_client(user),
    }