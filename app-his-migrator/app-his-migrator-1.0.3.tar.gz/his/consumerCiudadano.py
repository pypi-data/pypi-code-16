from django.db import models
import requests
from django.conf import settings

class CiudadanoRest(models.Model):

	_url = settings.URL_WS_REST_CIUDADANO 

	ESTADO_CIVIL_CHOICES = {"1":"S","2":"C","3":"S","4":"D","5":"V"}
	TIPO_DOC_CHOICES = {"0":"5","1":"1","2":"2","3":"3","4":"4"}

	def getPersonaPorDni(self, dni):

		response = requests.get('{0}/ciudadanos/ver/{1}/'.format(self._url,dni))

		json_attributes= response.json()['data']['attributes']

		mapper_persona= {}
		mapper_persona['idtipodoc']= self.TIPO_DOC_CHOICES[json_attributes['tipo_documento_minsa']]
		mapper_persona['nrodocumento']=json_attributes['numero_documento']
		mapper_persona['apepaterno']=json_attributes['apellido_paterno']
		mapper_persona['apematerno']=json_attributes['apellido_materno']
		mapper_persona['nombres']=json_attributes['nombres']
		
		if json_attributes.has_key('fecha_nacimiento'):
			mapper_persona['fechanacimiento']=json_attributes['fecha_nacimiento']

		if json_attributes['sexo']=="1":
			mapper_persona['idsexo']="M"
		else:
			mapper_persona['idsexo']="F"
		
		if json_attributes.has_key('etnia'):
			mapper_persona['idetnia']=json_attributes['etnia']
		
		mapper_persona['idubigeonacimiento']=''
		
		if json_attributes.has_key('get_distrito_domicilio_ubigeo_reniec'):
			mapper_persona['idubigeoresidencia']=json_attributes['get_distrito_domicilio_ubigeo_reniec']
		
		if json_attributes.has_key('get_distrito_domicilio_ubigeo_reniec'):
			mapper_persona['idubigeoresidencia_actual']=json_attributes['get_distrito_domicilio_ubigeo_reniec']
		
		if json_attributes.has_key('domicilio_direccion'):
			mapper_persona['domicilioresidencia']=json_attributes['domicilio_direccion']
		
		if json_attributes.has_key('domicilio_direccion'):
			mapper_persona['domicilioresidenciaactual']=json_attributes['domicilio_direccion']
		
		if json_attributes.has_key('grado_instruccion'):
			mapper_persona['idgradoinstruccion']=json_attributes['grado_instruccion']
		
		if json_attributes.has_key('estado_civil'):
			mapper_persona['idestadocivil']=self.ESTADO_CIVIL_CHOICES[json_attributes['estado_civil']]
		
		mapper_persona['idpais']=''
		mapper_persona['idestablecimiento']=''
		
		return mapper_persona