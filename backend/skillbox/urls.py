from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authenticate.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(
        'api/v1/schema/redoc',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]
