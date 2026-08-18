from rest_framework.permissions import BasePermission


class AutomationCreateOrStaff(BasePermission):
    """Staff has full access; the n8n service identity may only create logs.

    This prevents a leaked automation credential from approving supplier
    updates, editing conversations or accessing dashboard management data.
    """

    message = 'A automação pode apenas criar registros; esta ação exige um usuário administrador.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return getattr(view, 'action', None) == 'create' and request.user.username == 'n8n-bot'
