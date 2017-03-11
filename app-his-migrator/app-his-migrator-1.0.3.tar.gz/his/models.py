from django.db import models
from django.utils import timezone

class TramaHis(models.Model):
	id_model_base= models.IntegerField(default=0)
	id_cita_his = models.IntegerField(default=0)
	estado_enviado = models.CharField(max_length=10)
	estado_descripcion = models.TextField(null=True)
	trama_paciente_json = models.TextField(null=True)
	trama_personal_registra_json = models.TextField(null=True)
	trama_personal_atiende_json = models.TextField(null=True)
	trama_cita_json = models.TextField(null=True)
	enviado = models.BooleanField(default=False)
	fechaCreacion = models.DateTimeField(auto_now_add=True, editable=False)
	fechaEnviado = models.DateTimeField(default=timezone.now,null=True)
	nro_intentos = models.IntegerField(default=0)
