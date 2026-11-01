from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_web.urls')),
    path('algorithmique/', include('app_algs.urls')),
    path('python/', include('app_python.urls')),
]

# Servir les fichiers média en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)