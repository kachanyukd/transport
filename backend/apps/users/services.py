# User management is handled directly by UserViewSet + User model manager.
# No separate service class needed — user lifecycle operations are straightforward CRUD
# without complex business rules that would justify an extra indirection layer.
