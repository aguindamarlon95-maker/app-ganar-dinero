from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal # Importante para manejar dinero exacto

# 1. PERFIL (Saldo y Referidos)
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)
    # Nuevo campo: ¿Quién invitó a este usuario?
    invitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitados')

    def __str__(self):
        return f"{self.usuario.username} - ${self.saldo}"

# 2. TAREA
class Tarea(models.Model):
    OPCIONES_MODO = [('FOTO', '📸 Foto (Manual)'), ('TIMER', '⏳ Temporizador (Automático)')]
    tipo = models.CharField(max_length=50) 
    descripcion = models.TextField()
    pago_por_accion = models.DecimalField(max_digits=10, decimal_places=3)
    url_objetivo = models.URLField()
    modo = models.CharField(max_length=20, choices=OPCIONES_MODO, default='FOTO') 
    segundos_espera = models.IntegerField(default=0)

    def __str__(self): return f"{self.tipo} - ${self.pago_por_accion}"

# 3. PRUEBA
class Prueba(models.Model):
    trabajador = models.ForeignKey(User, on_delete=models.CASCADE)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    archivo = models.ImageField(upload_to='evidencias/', blank=True, null=True)
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)
    pagada = models.BooleanField(default=False)

    def __str__(self): return f"{self.trabajador.username} - {self.tarea.tipo}"

# 4. RETIRO
class Retiro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=3)
    metodo = models.CharField(max_length=50, default='PayPal') 
    cuenta = models.CharField(max_length=100, default='') 
    titular = models.CharField(max_length=100, default='') 
    fecha = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)

    def __str__(self): return f"{self.usuario.username} - ${self.monto}"

# --- SEÑALES (PAGOS AUTOMÁTICOS) ---
@receiver(post_save, sender=Prueba)
def pagar_tarea_aprobada(sender, instance, **kwargs):
    if instance.aprobada and not instance.pagada:
        perfil = Perfil.objects.get(usuario=instance.trabajador)
        perfil.saldo += instance.tarea.pago_por_accion
        perfil.save()
        Prueba.objects.filter(id=instance.id).update(pagada=True)