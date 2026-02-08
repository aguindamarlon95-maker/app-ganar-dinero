from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ESTA LÍNEA ES LA CLAVE: Conecta el servidor con tu app
    path('api/', include('core.urls')),
]