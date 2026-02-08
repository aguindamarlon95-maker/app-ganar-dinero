from django.contrib import admin
from django.urls import path, include
from core.views import subir_evidencia_web  # <--- IMPORTANTE: Traemos la función aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),     # Las rutas de datos siguen aquí
    path('subir/', subir_evidencia_web),    # <--- ¡EL ATAJO NUEVO! (Directo al grano)
]