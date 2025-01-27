from rest_framework import permissions

class CarteiraUsuarioPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if view.action == 'list':
            view.queryset = view.queryset.filter(usuario=request.user)
            return True
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        return obj.usuario == request.user
    
    
class UsuarioPermission(permissions.BasePermission):
    # Filtra e lista os usuários cujo ID é diferente do usuário autenticado.
    def has_permission(self, request, view):
        if view.action == 'list':
            view.queryset = view.queryset.exclude(id=request.user.id)
            return True
        
        # Para outras permissões gerais, delega ao comportamento padrão.
        return super().has_permission(request, view) and request.user.is_authenticated

    # Garante que apenas o usuário autenticado possa realizar operações nos seus próprios dados.
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
    

class UsuarioTransferenciaPermission(permissions.BasePermission):
    """
    Permissão personalizada para listar, obter e criar transferências apenas para o usuário autenticado.
    """

    def has_permission(self, request, view):
        """
        Verifica se o usuário tem permissão para acessar a ação solicitada.
        Permite apenas listagem, visualização e criação para usuários autenticados.
        """
        if view.action in ['list', 'retrieve', 'create']:
            # Verifica se o usuário está autenticado
            return request.user and request.user.is_authenticated
        
        # Para outras ações, a permissão é negada
        return False

    def has_object_permission(self, request, view, obj):
        """
        Garante que o usuário só pode acessar transferências em que ele é o remetente ou o destinatário.
        """
        if view.action in ['retrieve']:
            # Permite acesso se o usuário for o remetente ou destinatário da transferência
            return obj.usuario_origem == request.user or obj.usuario_destino == request.user

        # Para outras ações, nega a permissão
        return False

