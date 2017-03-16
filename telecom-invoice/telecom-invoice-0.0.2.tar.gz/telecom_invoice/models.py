# coding=utf-8

from fields import Field, IntegerField, CharField, ChecksumField, DateField, DecimalField


class AbstractFile(object):
    def calculate_authentication_code(self, *fields):
        pass

    @property
    def fields(self):
        fields = [getattr(self, field) for field in self.__dict__]
        fields = [field for field in fields if isinstance(field, Field)]
        fields = sorted(fields, key=lambda field: field.position[0])
        return fields

    def serialize(self):
        serialized = u"".join([field.serialize() for field in self.fields])
        return serialized + "\r\n"


class Master(AbstractFile):

    def __init__(self):
        # 1 CPF ou CNPJ | len 14 | 1-14 | int
        self.registration = IntegerField((1, 14))
        # 2 Inscrição Estadual | len 14 | 15-28 | str
        self.state_subscription = CharField((15, 28), "ISENTO")
        # 3 Razão Social | len 35 | 29-63 | str
        self.legal_name = CharField((29, 63))
        # 4 UF | len 2 | 64-65 | str
        self.state_code = CharField((64, 65))
        # 5 Classe de Consumo ou Tipo de Assinante | len 1 | 66-66 | int
        self.subscription_type = IntegerField(66)
        # 6 Fase ou Tipo de Utilização | len 1 | 67-67 | int
        self.utilization_type = IntegerField(67)
        # 7 Grupo de Tensão | len 2 | 68-69 | int
        self.tension_group = IntegerField((68, 69))
        # 8 Código de identificação do consumidor ou assinante | len 12 | 70-81 | str
        self.client_identification = CharField((70, 81))
        # 9 Data de emissão | len 8 | 82-89 | int
        self.emission_date = DateField((82, 89))
        # 10 Modelo | len 2 | 90-91 | int
        self.model = IntegerField((90, 91))
        # 11 Série | len 3| 92-94 | str
        self.series = CharField((92, 94))
        # 12 Número | len 9 | 95-103 | int
        self.number = IntegerField((95, 103))
        # 13 Código de Autenticação Digital documento fiscal | len 32 | 104-135 | str
        self.fiscal_document_authentication_code = ChecksumField((104, 135), self, fields=['registration', 'number', 'total_amount', 'bcicms', 'icms', 'emission_date', 'emitente_cnpj'])
        # 14 Valor total (com 2 decimais) | len 12 | 136-147 | int
        self.total_amount = DecimalField((136, 147))
        # 15 BCICMS (com 2 decimais) | len 12 | 148-159 | int
        self.bcicms = DecimalField((148, 159))
        # 16 ICMS destacado (com 2 decimais) | len 12 | 160-171 | int
        self.icms = DecimalField((160, 171))
        # 17 Operações isentas ou não tributadas (com 2 decimais) | len 12 | 172-183 | int
        self.not_taxed_operations = DecimalField((172, 183))
        # 18 Outros valores (com 2 decimais) | len 12 | 184-195 | int
        self.other_amount = DecimalField((184, 195))
        # 19 Situação do documento | len 1 | 196-196 | str
        self.situation = CharField(196)
        # 20 Ano e Mês de referência de apuração | len 4| 197-200 | int
        self.year_month_apuration = DateField((197, 200), date_format="%y%m")
        # 21 Referência ao item da NF | len 9 | 201-209 | int
        self.invoice_item_reference = IntegerField((201, 209))
        # 22 Número do terminal telefônico ou Número da conta de consumo | len 12 | 210-221 | str
        self.phone_number = CharField((210, 221))
        # 23 Indicação do tipo de informação contida no campo 1 | len 1 | 222-222 | int
        self.registration_type = IntegerField(222)
        # 24 Tipo de cliente | len 2 | 223-224 | int
        self.client_type = IntegerField((223, 224))
        # 25 Subclasse de consumo | len 2 | 225-226 | int
        self.consumption_subclass = IntegerField((225, 226))
        # 26 Número do terminal telefônico principal | len 12 | 227-238 | str
        self.main_phone_number = CharField((227, 238))
        # 27 CNPJ do emitente | len 14 | 239-252 | int
        self.emitente_cnpj = IntegerField((239, 252))
        # 28 Número ou código da fatura comercial | len 20 | 253-272 | str
        self.billing_number = CharField((253, 272))
        # 29 Valor total da fatura comercial | len 12 | 273-284 | int
        self.billing_total = DecimalField((273, 284))
        # 30 Data de leitura anterior | len 8 | 285-292 | int
        self.last_reading = DateField((285, 292), blank='0')
        # 31 Data de leitura atual | len 8 | 293-300 | int
        self.current_reading = DateField((293, 300), blank='0')
        # 32 Brancos - reservado para uso futuro | len 50 | 301-350 | str
        # Campo 32 - Informar a chave de acesso do documento fiscal eletrônico (CV115-e).
        # Nas unidades federadas em que tal documento não tiver sido implementado, preencher com brancos;
        self.access_key = CharField((301, 350))
        # 33 Brancos - reservado para uso futuro | len 8 | 351-358 | int
        # Campo 33 - Informar a data da autorização de emissão do documento fiscal eletrônico
        # (CV115-e).Nas unidades federadas em que tal documento não tiver sido implementado, preencher com zeros;
        self.authorization_date = DateField((351, 358), blank='0')
        # 34 Informações adicionais | len 30 | 359-388 | str
        self.additional_information = CharField((359, 388))
        # 35 Brancos - reservado para uso futuro | len 5 | 389-393 | str
        self.blanks = CharField((389, 393))
        # 36 Código de autenticação Digital do registro | len 32 | 394-425 | str
        self.digital_register_authentication_code = ChecksumField((394, 425), self)


class Item(AbstractFile):
    def __init__(self):
        # 1 CNPJ ou CPF | len 14 | 1-14 | int
        self.registration = IntegerField((1, 14))
        # 2 UF | len 2 | 15-16 | str
        self.state_code = CharField((15, 16))
        # 3 Classe de Consumo ou Tipo de Assinante | len 1 | 17-17 | int
        self.subscription_type = IntegerField(17)
        # 4 Fase ou Tipo de Utilização | len 1 | 18-18 | int
        self.utilization_type = IntegerField(18)
        # 5 Grupo de Tensão | len 2 | 19-20 | int
        self.tension_group = IntegerField((19, 20))
        # 6 Data de Emissão | len 8 | 21-28 | int
        self.emission_date = DateField((21, 28))
        # 7 Modelo | len 2 | 29-30 | str
        self.model = CharField((29, 30))
        # 8 Série | len 3 | 31-33 | str
        self.series = CharField((31, 33))
        # 9 Número | len 9 | 34-42 | int
        self.number = IntegerField((34, 42))
        # 10 CFOP | len 4 | 43-46 | int
        self.cfop = IntegerField((43, 46))
        # 11 Item | len 3 | 47-49 | int
        self.item = IntegerField((47, 49))
        # 12 Código de serviço ou fornecimento | len 10 | 50-59 | str
        self.item_code = CharField((50, 59))
        # 13 Descrição do serviço ou fornecimento | len 40 | 60-99 | str
        self.item_description = CharField((60, 99))
        # 14 Código de classificação do item| len 4 | 100-103 | int
        self.item_classification = IntegerField((100, 103))
        # 15 Unidade | len 6 | 104-109 | str
        self.unit = CharField((104, 109))
        # 16 Quantidade contratada (com 3 decimais) | len 12 | 110-121 | int
        self.requested_quantity = DecimalField((110, 121), precision=3)
        # 17 Quantidade prestada ou fornecida (com 3 decimais) | len 12 | 122-133 | int
        self.provided_quantity = DecimalField((122, 133), precision=3)
        # 18 Total (com 2 decimais) | len 11 | 134-144 | int
        self.total_amount = DecimalField((134, 144))
        # 19 Desconto (com 2 decimais) | len 11 | 145-155 | int
        self.discount = DecimalField((145, 155))
        # 20 Acréscimo e Despesas Acessoriais (com 2 decimais) | len 11 | 156-166 | int
        self.accessory_expenses = DecimalField((156, 166))
        # 21 BC ICMS (com 2 decimais) | len 11 | 167-177 | int
        self.bcicms = DecimalField((167, 177))
        # 22 ICMS (com 2 decimais) | len 11 | 178-188 | int
        self.icms = DecimalField((178, 188))
        # 23 Operações Isentas ou não tributadas (com 2 decimais) | len 11 | 189-199 | int
        self.not_taxed_operations = DecimalField((189, 199))
        # 24 Outros valores que não compõe a BC do ICMS (com 2 decimais) | len 11 | 200-210 | int
        self.other_amount = DecimalField((198, 208))
        # 25 Alíquota do ICMS (com 2 decimais) | len 4 | 211-214 | int
        self.icms_aliquote = DecimalField((211, 214))
        # 26 Situação | len 1 | 215-215 | str
        self.situation = CharField(215)
        # 27 Ano e Mês de referência de apuração | len 4 | 216-219 | str
        self.year_month_apuration = DateField((216, 219), date_format="%y%m")
        # 28 Número do contrato | len 15 | 220-234 | str
        self.contract_number = CharField((220, 234))
        # 29 Quantidade faturada (com 3 decimais) | len 12 | 235-246 | int
        self.billing_quantity = DecimalField((235, 246), precision=3)
        # 30 Tarifa aplicada / preço médio efetivo (com 6 decimais) | len 11 | 247-257 | int
        self.billing_price = DecimalField((247, 257), precision=6)
        # 31 Alíquota PIS/PASEP (com 4 decimais) | len 6 | 258-263 | int
        self.pis_pasep_aliquot = DecimalField((258, 263), precision=4)
        # 32 PIS/PASEP (com 2 decimais) | len 11 | 264-274 | int
        self.pis_pasep = DecimalField((264, 274), precision=2)
        # 33 Alíquota COFINS (com 4 decimais) | len 6 | 275-280 | int
        self.confins_aliquot = DecimalField((275, 280), precision=4)
        # 34 COFINS (com 2 decimais) | len 11 | 281-291 | int
        self.cofins = DecimalField((281, 291), precision=2)
        # 35 Indicador de desconto judicial | len 1 | 292-292 | int
        self.judicial_discount = CharField(292)
        # 36 Tipo de isenção / redução de base de cálculo| len 2 | 293-294 | int
        self.exemption_type = IntegerField((293, 294))
        # 37 Brancos - reservado para uso futuro | len 5 | 295-299 | str
        self.blanks = CharField((295, 299))
        # 38 Código de Autenticação Digital do registro | len 32 | 300-331 | str
        self.digital_register_authentication_code = ChecksumField((300, 331), self)


class Register(AbstractFile):
    def __init__(self):
        # 1 CNPJ ou CPF | len 14 | 1-14 | int
        self.registration = IntegerField((1, 14))
        # 2 IE | len 14 | 15-28 | str
        self.state_subscription = CharField((15, 28), "ISENTO")
        # 3 Razão Social | len 35 | 29-63 | str
        self.legal_name = CharField((29, 63))
        # 4 Logradouro | len 45 | 64-108 | str
        self.street = CharField((64, 108))
        # 5 Número | len 5 | 109-113 | int
        self.number = IntegerField((109, 113))
        # 6 Complemento | len 15 | 114-128 | str
        self.complement = CharField((114, 128))
        # 7 CEP | len 8 | 129-136 | int
        self.zip_code = IntegerField((129, 136))
        # 8 Bairro | len 15 | 137-151 | str
        self.neighborhood = CharField((137, 151))
        # 9 Município | len 30 | 152-181 | str
        self.city = CharField((152, 181))
        # 10 UF | len 2 | 182-183 | str
        self.state_code = CharField((182, 183))
        # 11 Telefone de contato | len 12 | 184-195 | int
        self.phone = CharField((184, 195))
        # 12 Código de Identificação do consumidor ou assinante | len 12 | 196-207 | str
        self.client_code = CharField((196, 207))
        # 13 Número do terminal telefônico ou Número de conta do consumo | len 12 | 208-219 | str
        self.contract_code = CharField((208, 219))
        # 14 UF de habilitação do terminal telefônico | len 2 | 220-221 | str
        self.contract_state = CharField((220, 221))
        # 15 Data de emissão | len 8 | 222-229 | int
        self.emission_date = DateField((222, 229))
        # 16 Modelo  | len 2 | 230-231 | int
        self.model = IntegerField((230, 231))
        # 17 Série  | len 3 | 232-234 | str
        self.series = CharField((232, 234))
        # 18 Número  | len 9 | 235-243 | int
        self.sequential_number = IntegerField((235, 243))
        # 19 Código do município  | len 7 | 244-250 | int
        self.city_code = IntegerField((244, 250))
        # 20 Brancos - reservado para uso futuro | len 5 | 251-255 | str
        self.blanks = CharField((251, 255))
        # 21 Código de Autenticação Digital do registro | len 32 | 256-287 | str
        self.digital_register_authentication_code = ChecksumField((256, 287), self)
