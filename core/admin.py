from django.contrib import admin
from .models import Tarea, Perfil, Prueba, Retiro  # <--- Agregamos Retiro aquí

admin.site.register(Tarea)
admin.site.register(Perfil)
admin.site.register(Prueba)
admin.site.register(Retiro)  # <--- Y lo registramos aquí