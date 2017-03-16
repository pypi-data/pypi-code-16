# coding=latin1
from os import path
import codecs
from decimal import Decimal
from datetime import date

from telecom_invoice.models import Master

FIXTURES = path.join(path.dirname(__file__), "fixtures")


def test_master():
    master = Master()
    # 1 CPF ou CNPJ | len 14 | 1-14 | int
    master.registration.value = 47827332000108
    # 2 Inscrição Estadual | len 14 | 15-28 | str
    master.state_subscription.value = "492175108116"
    # 3 Razão Social | len 35 | 29-63 | str
    master.legal_name.value = "Agro  Safra Ind e Com de Adubos Ltd"
    # 4 UF | len 2 | 64-65 | str
    master.state_code.value = "SP"
    # 5 Classe de Consumo ou Tipo de Assinante | len 1 | 66-66 | int
    master.subscription_type.value = 1
    # 6 Fase ou Tipo de Utilização | len 1 | 67-67 | int
    master.utilization_type.value = 4
    # 7 Grupo de Tensão | len 2 | 68-69 | int
    master.tension_group.value = 00
    # 8 Código de identificação do consumidor ou assinante | len 12 | 70-81 | str
    master.client_identification.value = "1079"
    # 9 Data de emissão | len 8 | 82-89 | int
    master.emission_date.value = date(2014, 03, 06)
    # 10 Modelo | len 2 | 90-91 | int
    master.model.value = 22
    # 11 Série | len 3| 92-94 | str
    master.serie.value = "001"
    # 12 Número | len 9 | 95-103 | int
    master.number.value = 10789
    # 14 Valor total (com 2 decimais) | len 12 | 136-147 | int
    master.total_amount.value = Decimal("89.90")
    # 15 BCICMS (com 2 decimais) | len 12 | 148-159 | int
    master.bcicms.value = Decimal("0")
    # 16 ICMS destacado (com 2 decimais) | len 12 | 160-171 | int
    master.icms.value = Decimal("0")
    # 17 Operações isentas ou não tributadas (com 2 decimais) | len 12 | 172-183 | int
    master.not_taxed_operations.value = Decimal("0")
    # 18 Outros valores (com 2 decimais) | len 12 | 184-195 | int
    master.other_amount.value = Decimal("0")
    # 19 Situação do documento | len 1 | 196-196 | str
    master.situation.value = "N"
    # 20 Ano e Mês de referência de apuração | len 4| 197-200 | int
    master.year_month_apuration.value = date(2014, 03, 06)
    # 21 Referência ao item da NF | len 9 | 201-209 | int
    master.invoice_item_reference.value = 1
    # 22 Número do terminal telefônico ou Número da conta de consumo | len 12 | 210-221 | str
    master.phone_number.value = "1136875766"

    with codecs.open(path.join(FIXTURES, "SP0011403NM.001"), "r", encoding="latin1") as f:
        assert master.serialize() == f.read()
