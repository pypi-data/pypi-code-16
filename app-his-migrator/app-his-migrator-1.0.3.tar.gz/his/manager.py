from django.db import models
from his.models import TramaHis
from his.consumerCiudadano import CiudadanoRest
from his.consumerHis import HisRest
from django.utils import timezone
import json

class HisManager(models.Manager):

	ciudadano_rest = CiudadanoRest()
	his_rest = HisRest()

	def generate(self, instanceObject, schemaTramaHis):
		
		tramaHis = TramaHis()

		try:
			tramaHis.id_model_base= instanceObject.id
			tramaHis.nro_intentos += 1 
			
			mapper_paciente= self.getMapperPaciente(instanceObject,schemaTramaHis)
			mapper_personal_registra = self.getMapperPersonal(instanceObject,schemaTramaHis,'personal_registra')
			mapper_personal_atiende = self.getMapperPersonal(instanceObject,schemaTramaHis,'personal_atiende')
			mapper_cita =  self.getMapperCita(instanceObject,schemaTramaHis)

			tramaHis.trama_paciente_json = str(json.dumps(mapper_paciente))
			tramaHis.trama_personal_registra_json = str(json.dumps(mapper_personal_registra))
			tramaHis.trama_personal_atiende_json = str(json.dumps(mapper_personal_atiende))
			tramaHis.trama_cita_json = str(json.dumps(mapper_cita))

			response_paciente= self.his_rest.post_paciente(mapper_paciente)
			
			tramaHis.estado_enviado = response_paciente['estado']
			tramaHis.estado_descripcion = response_paciente['descripcion'].encode("utf-8")

			
			if response_paciente['estado'] in ('OK'):

				id_paciente = response_paciente['idpaciente']
				
				response_personal_registra =  self.his_rest.post_personal(mapper_personal_registra)
				

				tramaHis.estado_enviado = response_personal_registra['estado']
				tramaHis.estado_descripcion = response_personal_registra['descripcion'].encode("utf-8")

				

				if response_personal_registra['estado'] in ('OK'):

					id_personal_registra = response_personal_registra['idpersonal']
					
					response_personal_atiende =  self.his_rest.post_personal(mapper_personal_atiende)

					tramaHis.estado_enviado = response_personal_atiende['estado']
					tramaHis.estado_descripcion = response_personal_atiende['descripcion'].encode("utf-8")
				
					if response_personal_atiende['estado'] in ('OK'):

						id_personal_atiende = response_personal_atiende['idpersonal']

						query = TramaHis.objects.filter(id_model_base=instanceObject.id, id_cita_his__gte=0).order_by('-id')[:1]

						if len(query.values())==1:
							mapper_cita["idcita"] = query.values()[0]["id_cita_his"]


						mapper_cita["idpaciente"] = int(id_paciente)
						mapper_cita["idpersonalregistra"]= int(id_personal_registra)
						mapper_cita["idpersonalatiende"]= int(id_personal_atiende)
					
						tramaHis.trama_cita_json = str(json.dumps(mapper_cita))

						response_cita = self.his_rest.post_cita(mapper_cita)

						tramaHis.estado_enviado = response_cita['estado']
						tramaHis.estado_descripcion = response_cita['descripcion'].encode("utf-8")
					

						if response_cita['estado'] in ('OK'):
							id_cita = response_cita['idcita']	
							tramaHis.id_cita_his = 	id_cita	
							tramaHis.enviado = True
							tramaHis.fechaEnviado = timezone.now()

							print("id cita: {}".format(id_cita))
		except Exception as e:
			print("Exception: {}".format(str(e.args)))
			tramaHis.estado_descripcion = str(e.args)
		

		#import pdb;
		#pdb.set_trace()
		tramaHis.save()

		return True

	def generate_old(self, instanceObject, schemaTramaHis):
		
		tramaHis = TramaHis()

		try:
			tramaHis.id_model_base= instanceObject.id

			mapper_persona= self.getMapperPaciente(instanceObject,schemaTramaHis)
			response_paciente= self.his_rest.post_paciente(mapper_persona)
		
			tramaHis.estado_enviado = response_paciente['estado']
			tramaHis.estado_descripcion = response_paciente['descripcion'].encode("utf-8")


			if response_paciente['estado'] in ('OK'):

				id_paciente = response_paciente['idpaciente']
				mapper_personal_registra = self.getMapperPersonal(instanceObject,schemaTramaHis,'personal_registra')
				response_personal_registra =  self.his_rest.post_personal(mapper_personal_registra)

				#import pdb;
				#pdb.set_trace()

				tramaHis.estado_enviado = response_personal_registra['estado']
				tramaHis.estado_descripcion = response_personal_registra['descripcion'].encode("utf-8")

				if response_personal_registra['estado'] in ('OK'):

					id_personal_registra = response_personal_registra['idpersonal']
					mapper_personal_atiende = self.getMapperPersonal(instanceObject,schemaTramaHis,'personal_atiende')
					response_personal_atiende =  self.his_rest.post_personal(mapper_personal_atiende)

					tramaHis.estado_enviado = response_personal_atiende['estado']
					tramaHis.estado_descripcion = response_personal_atiende['descripcion'].encode("utf-8")
				
					if response_personal_atiende['estado'] in ('OK'):

						id_personal_atiende = response_personal_atiende['idpersonal']

						mapper_cita =  self.getMapperCita(instanceObject,schemaTramaHis)
						#import pdb;
						#pdb.set_trace()

						query = TramaHis.objects.filter(id_model_base=instanceObject.id, id_cita_his__gte=0).order_by('-id')[:1]

						if len(query.values())==1:
							mapper_cita["idcita"] = query.values()[0]["id_cita_his"]


						mapper_cita["idpaciente"] = int(id_paciente)
						mapper_cita["idpersonalregistra"]= int(id_personal_registra)
						mapper_cita["idpersonalatiende"]= int(id_personal_atiende)
					
						tramaHis.tramaJson= str(json.dumps(mapper_cita))

						response_cita = self.his_rest.post_cita(mapper_cita)

						tramaHis.estado_enviado = response_cita['estado']
						tramaHis.estado_descripcion = response_cita['descripcion'].encode("utf-8")
					

						if response_cita['estado'] in ('OK'):
							id_cita = response_cita['idcita']	
							tramaHis.id_cita_his = 	id_cita	
							tramaHis.enviado = True
							tramaHis.fechaEnviado = timezone.now()

							print("id cita: {}".format(id_cita))
		except Exception as e:
			print("Exception: ".format(str(e.args)))
			tramaHis.estado_descripcion = str(e.args)
		

		#import pdb;
		#pdb.set_trace()
		tramaHis.save()

		return True


	def getMapperPaciente(self, instanceObject, schemaTramaHis):
		
		object_instance = instanceObject

		atri_paciente= schemaTramaHis['paciente']
		atri_paciente_id_tipo_doc = atri_paciente['id_tipo_doc']
		atri_paciente_nro_documento = atri_paciente['nro_documento']
		atri_paciente_hc = atri_paciente['historia_clinica']
		atri_establecimiento= schemaTramaHis['id_establecimiento']
		atri_id_sistema= schemaTramaHis["id_sistema"]

		mapper_persona =  self.ciudadano_rest.getPersonaPorDni(self.getValor(object_instance,atri_paciente_nro_documento))

		mapper_persona['idpais']='PER'
		mapper_persona['idestablecimiento']=self.getValor(object_instance,atri_establecimiento) 
		mapper_persona['idflag']=self.getValor(object_instance, atri_id_sistema)
		mapper_persona["nrohistoriaclinica"]=self.getValor(object_instance,atri_paciente_hc) 
		
		return mapper_persona


	def getMapperPersonal(self, instanceObject, schemaTramaHis, tipo):

		object_instance = instanceObject

		atri_personal= schemaTramaHis[tipo]
		atri_personal_id_tipo_doc = atri_personal['id_tipo_doc']
		atri_personal_nro_documento = atri_personal['nro_documento']
		atri_personal_id_profesion = atri_personal['id_profesion']
		atri_personal_id_condicion = atri_personal['id_condicion']
		atri_establecimiento= schemaTramaHis['id_establecimiento']

		mapper_persona = self.ciudadano_rest.getPersonaPorDni(self.getValor(object_instance,atri_personal_nro_documento))
		del mapper_persona['idetnia']
		mapper_persona['idpais']='PER'
		mapper_persona['idestablecimiento']=self.getValor(object_instance,atri_establecimiento) 
		mapper_persona['idprofesion']=self.getValor(object_instance,atri_personal_id_profesion)
		mapper_persona['idcondicion']=self.getValor(object_instance,atri_personal_id_condicion)

		return mapper_persona


	def getMapperCita(self, instanceObject, schemaTramaHis):
		object_instance = instanceObject
		
		atri_cita_id_financiador = schemaTramaHis["id_financiador"]
		#atri_cita_fg_sis = schemaTramaHis["fg_sis"]
		atri_cita_componente = schemaTramaHis["componente"]
		atri_cita_fecha_atencion = schemaTramaHis["fecha_atencion"]
		atri_cita_id_turno = schemaTramaHis["id_turno"]
		atri_cita_id_tipcond_estab = schemaTramaHis["id_tipcond_estab"]
		atri_cita_id_tipcond_serv = schemaTramaHis["id_tipcond_serv"]
		atri_cita_id_ups = schemaTramaHis["id_ups"]
		atri_cita_id_tipedad_reg = schemaTramaHis["id_tipedad_reg"]
		atri_cita_id_establecimiento = schemaTramaHis["id_establecimiento"]
		atri_cita_edad_reg = schemaTramaHis["edad_reg"]
		atri_cita_num_afil = schemaTramaHis["num_afil"]
		atri_cita_annio_edad = schemaTramaHis["annio_edad"]
		atri_cita_mes_edad = schemaTramaHis["mes_edad"]
		atri_cita_dia_edad = schemaTramaHis["dia_edad"]
		atri_cita_items = schemaTramaHis["items"]
		atri_cita_id_sistema = schemaTramaHis["id_sistema"]
		

		mapper_cita = {}

		mapper_cita["idups"]=self.getValor(instanceObject,atri_cita_id_ups)
		mapper_cita["idestablecimiento"]=self.getValor(instanceObject,atri_cita_id_establecimiento)
		mapper_cita["fechaatencion"]="{:%Y%m%d}".format(self.getValor(instanceObject,atri_cita_fecha_atencion))
		mapper_cita["idturno"]=self.getValor(instanceObject,atri_cita_id_turno)
		mapper_cita["idfinanciador"]=self.getValor(instanceObject,atri_cita_id_financiador)
		mapper_cita["numeroafiliacion"]=self.getValor(instanceObject,atri_cita_num_afil)
		mapper_cita["componente"]=self.getValor(instanceObject,atri_cita_componente)		
		mapper_cita["idtipcondestab"]=self.getValor(instanceObject,atri_cita_id_tipcond_estab)
		mapper_cita["idtipcondserv"]=self.getValor(instanceObject,atri_cita_id_tipcond_serv) 
		mapper_cita["edadregistro"]=self.getValor(instanceObject,atri_cita_edad_reg)
		mapper_cita["idtipedadregistro"]=self.getValor(instanceObject,atri_cita_id_tipedad_reg)
		mapper_cita["estadoregistro"]="A"
		mapper_cita["annioedad"]=self.getValor(instanceObject,atri_cita_annio_edad) 
		mapper_cita["mesedad"]=self.getValor(instanceObject,atri_cita_mes_edad)
		mapper_cita["diaedad"]=self.getValor(instanceObject,atri_cita_dia_edad) 
		mapper_cita["fgdiag"]=self.getValor(instanceObject, atri_cita_id_sistema)
		mapper_cita["items"]=self.getValor(instanceObject,atri_cita_items)

		mapper_examen_fisico = self.getMapperExamenFisico(instanceObject, schemaTramaHis)

		mapper_cita["examenfisico"] = mapper_examen_fisico

		
		return mapper_cita

	def getMapperExamenFisico(self, instanceObject, schemaTramaHis):

		atri_examen_fisico = schemaTramaHis["examen_fisico"]

		atri_examfisico_peso = atri_examen_fisico["peso"]
		atri_examfisico_talla = atri_examen_fisico["talla"]
		atri_examfisico_hemoglobina = atri_examen_fisico["hemoglobina"]

		mapper_examen_fisico = {}
		mapper_examen_fisico["peso"] = self.getValor(instanceObject, atri_examfisico_peso)
		mapper_examen_fisico["talla"] = self.getValor(instanceObject, atri_examfisico_talla)
		mapper_examen_fisico["hemoglobina"] = self.getValor(instanceObject, atri_examfisico_hemoglobina)

		return mapper_examen_fisico

	def getValor(self, instanceObject, param):

		#import pdb;
		#pdb.set_trace()

		if isinstance(param,dict):
			rel = param['rel']
			prop = param['prop']

			valor = getattr(getattr(instanceObject,rel),prop)
			return valor
		else:
			if param=="":
				valor = None
			else:
				valor = getattr(instanceObject,param)
			return valor
