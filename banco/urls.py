from rest_framework.routers import DefaultRouter
from .views import CarteiraViewSet,UsuarioViewSet,TransferenciaViewSet

router = DefaultRouter()
router.register(r'carteiras', CarteiraViewSet, basename='cateira')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'transferencias', TransferenciaViewSet, basename='transferencia')


urlpatterns = router.urls
