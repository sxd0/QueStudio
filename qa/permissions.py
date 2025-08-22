from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        author = getattr(obj, "author", None)
        return bool(user.is_staff or (author and author_id(author) == user.id))

def author_id(author):
    try:
        return author.id
    except Exception:
        return None
