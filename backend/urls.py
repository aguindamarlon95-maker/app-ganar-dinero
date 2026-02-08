from django.contrib import admin
from django.urls import path, include
from core.views import subir_evidencia_web
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('subir/', subir_evidencia_web),
]

# ESTO ES LO NUEVO: Permite ver las fotos subidas
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)