from rest_framework import serializers
from .models import Tarea, Perfil, Prueba

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = '__all__'

# --- ESTO ES LO NUEVO ---
class PruebaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prueba
        fields = '__all__'
from rest_framework import serializers
from .models import Tarea, Perfil, Prueba

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ['id', 'usuario', 'saldo']  # <--- IMPORTANTE: Aquí viaja el dinero

class PruebaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prueba
        fields = '__all__'
# ... (al final del archivo, agrega la clase Retiro) ...
from .models import Retiro # <--- Asegúrate de importar Retiro arriba o agrégalo aquí

class RetiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retiro
        fields = '__all__'