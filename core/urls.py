from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importamos TODAS tus funciones
from .views import (
    TareaViewSet, PerfilViewSet, PruebaViewSet, RetiroViewSet,
    login_usuario, registrar_usuario, 
    reclamar_recompensa_automatica, solicitar_retiro, subir_evidencia_web
)

# Rutas automáticas (Base de datos)
router = DefaultRouter()
router.register(r'tareas', TareaViewSet)
router.register(r'perfiles', PerfilViewSet)
router.register(r'pruebas', PruebaViewSet)
router.register(r'retiros', RetiroViewSet)

# Rutas manuales (Login, Registro, etc.)
urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_usuario),
    path('registro/', registrar_usuario),
    path('reclamar_auto/', reclamar_recompensa_automatica),
    path('solicitar_retiro/', solicitar_retiro),
    path('subir/', subir_evidencia_web),
]