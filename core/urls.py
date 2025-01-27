from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views



urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/token/', jwt_views.TokenObtainPairView.as_view(),name='token_obtain_pair'),

    path('api/v1/token/refresh/', jwt_views.TokenRefreshView.as_view(),name='token_refresh'),

    path('api/v1/', include('banco.urls')),
]

#Isso fará com que o Django sirva os arquivos estáticos diretamente enquanto estiver no modo de desenvolvimento.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
