from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Tarea, Perfil, Prueba, Retiro
from .serializers import TareaSerializer, PerfilSerializer, PruebaSerializer, RetiroSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal # Para sumar dinero exacto

# --- VIEWSETS ---
class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all(); serializer_class = TareaSerializer
class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all(); serializer_class = PerfilSerializer
class PruebaViewSet(viewsets.ModelViewSet):
    queryset = Prueba.objects.all(); serializer_class = PruebaSerializer
class RetiroViewSet(viewsets.ModelViewSet):
    queryset = Retiro.objects.all(); serializer_class = RetiroSerializer

# --- API ---
@api_view(['POST'])
def login_usuario(request):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    if user: return Response({"id": user.id, "nombre": user.first_name, "mensaje": "Login exitoso"})
    return Response({"error": "Credenciales inválidas"}, status=400)

@api_view(['POST'])
def registrar_usuario(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        codigo_invitacion = request.data.get('codigo_invitacion', '').strip() # <--- NUEVO
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Usuario ya existe"}, status=400)
        
        # 1. Crear Usuario
        user = User.objects.create_user(username=username, password=password)
        user.first_name = username
        user.save()
        
        # 2. Crear Perfil y Verificar Invitación
        perfil_nuevo = Perfil.objects.create(usuario=user, saldo=0.000)
        
        mensaje_extra = ""
        if codigo_invitacion:
            try:
                # Buscamos al Padrino (quien invitó)
                padrino = User.objects.get(username=codigo_invitacion)
                perfil_padrino = Perfil.objects.get(usuario=padrino)
                
                # Le damos su premio al Padrino ($0.10)
                perfil_padrino.saldo += Decimal('0.100')
                perfil_padrino.save()
                
                # Guardamos la relación
                perfil_nuevo.invitado_por = padrino
                perfil_nuevo.save()
                
                mensaje_extra = f" (Invitado por {padrino.username})"
            except User.DoesNotExist:
                pass # Si el código no existe, no pasa nada, se registra normal

        return Response({"mensaje": f"¡Bienvenido!{mensaje_extra}"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
def reclamar_recompensa_automatica(request):
    try:
        usuario = User.objects.get(id=request.data.get('usuario_id'))
        tarea = Tarea.objects.get(id=request.data.get('tarea_id'))
        if Prueba.objects.filter(trabajador=usuario, tarea=tarea).exists(): return Response({"error": "Ya completada"}, status=400)
        if tarea.modo != 'TIMER': return Response({"error": "Requiere foto"}, status=400)
        
        Prueba.objects.create(trabajador=usuario, tarea=tarea, aprobada=True, comentario="Auto Timer")
        perfil = Perfil.objects.get(usuario=usuario)
        perfil.saldo += tarea.pago_por_accion
        perfil.save()
        return Response({"mensaje": "OK"}, status=200)
    except Exception as e: return Response({"error": str(e)}, status=400)

@api_view(['POST'])
def solicitar_retiro(request):
    try:
        usuario = User.objects.get(id=request.data.get('usuario_id'))
        monto = float(request.data.get('monto', 0))
        perfil = Perfil.objects.get(usuario=usuario)
        if perfil.saldo < 1.00 or float(perfil.saldo) < monto: return Response({"error": "Saldo insuficiente"}, status=400)
        perfil.saldo = float(perfil.saldo) - monto
        perfil.save()
        Retiro.objects.create(usuario=usuario, monto=monto, metodo=request.data.get('metodo'), cuenta=request.data.get('cuenta'), titular=usuario.username)
        return Response({"mensaje": "Solicitud recibida", "nuevo_saldo": perfil.saldo})
    except Exception as e: return Response({"error": str(e)}, status=400)

@csrf_exempt
def subir_evidencia_web(request):
    if request.method == 'GET':
        return HttpResponse(f"""<html><body style='text-align:center; font-family:sans-serif; padding:20px;'>
            <h2>📸 Subir Evidencia</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="text" name="usuario_id" value="{request.GET.get('usuario_id','')}" readonly style="background:#eee; border:1px solid #ccc; padding:10px; width:100%; margin-bottom:10px;"><br>
                <input type="text" name="tarea_id" value="{request.GET.get('tarea_id','')}" readonly style="background:#eee; border:1px solid #ccc; padding:10px; width:100%; margin-bottom:10px;"><br>
                <input type="file" name="evidencia" required style="margin:20px 0;"><br>
                <button style="background:blue; color:white; padding:15px; border:none; border-radius:5px; width:100%;">ENVIAR</button>
            </form></body></html>""")
    if request.method == 'POST':
        try:
            u = User.objects.get(id=request.POST.get('usuario_id'))
            t = Tarea.objects.get(id=request.POST.get('tarea_id'))
            p = Prueba.objects.filter(trabajador=u, tarea=t).first()
            if p: p.archivo = request.FILES.get('evidencia'); p.save()
            else: Prueba.objects.create(trabajador=u, tarea=t, archivo=request.FILES.get('evidencia'))
            return HttpResponse("<h1 style='color:green; text-align:center;'>¡LISTO! ✅</h1>")
        except Exception as e: return HttpResponse(f"Error: {e}")