
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenObtainPairView, TokenBlacklistView
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

TokenObtainPairView.post = swagger_auto_schema(
    operation_id='User Login',
    operation_description='User Login',
    security=[],  # Set security to an empty list
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='username', default="ali"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='password',
                                       default="123"),
        },
        required=['username', 'password']
    )
)(TokenObtainPairView.post)

schema_view = get_schema_view(
    openapi.Info(
        title="Test Project API",
        default_version='v1',
        description="Test description",
        contact=openapi.Contact(email="testproject@snippets.local"),
        license=openapi.License(name="Test Project License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
admin.site.site_header = 'Test Project'
admin.site.index_title = 'Welcome to Test Project Administration'
admin.site.site_title = 'Test Project Administration'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
