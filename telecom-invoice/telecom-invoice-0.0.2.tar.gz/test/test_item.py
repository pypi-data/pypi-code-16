# coding=utf-8
from os import path
import codecs
from decimal import Decimal
from datetime import date

from telecom_invoice.models import Item

FIXTURES = path.join(path.dirname(__file__), "fixtures")


def test_item():
    item = Item()
    # 1 CNPJ ou CPF | len 14 | 1-14 | int
    item.registration.value = 47827332000108
    # 2 UF | len 2 | 15-16 | str
    item.state_code.value = "SP"
    # 3 Classe de Consumo ou Tipo de Assinante | len 1 | 17-17 | int
    item.subscription_type.value = 1
    # 4 Fase ou Tipo de Utilização | len 1 | 18-18 | int
    item.utilization_type.value = 4
    # 5 Grupo de Tensão | len 2 | 19-20 | int
    item.tension_group.value = 0
    # 6 Data de Emissão | len 8 | 21-28 | int
    item.emission_date.value = date(2014, 03, 06)
    # 7 Modelo | len 2 | 29-30 | str
    item.model.value = "22"
    # 8 Série | len 3 | 31-33 | str
    item.serie.value = "001"
    # 9 Número | len 9 | 34-42 | int
    item.number.value = 10789
    # 10 CFOP | len 4 | 43-46 | int
    item.cfop.value = 5303
    # 11 Item | len 3 | 47-49 | int
    item.item.value = 1
    # 13 Descrição do serviço ou fornecimento | len 40 | 60-99 | str
    item.item_description.value = "PRESTACAO DE SERVICOS DE ACESSO IP PARA "
    # 14 Código de classificação do item| len 4 | 100-103 | int
    item.item_classification.value = 104
    # 18 Total (com 2 decimais) | len 11 | 132-142 | int
    item.total_amount.value = Decimal("89.90")
    # 26 Situação | len 1 | 213-213 | str
    item.situation.value = "N"
    # 27 Ano e Mês de referência de apuração | len 4 | 214-217 | str
    item.year_month_apuration.value = date(2014, 03, 06)

    with codecs.open(path.join(FIXTURES, "SP0011403NI.001"), "r", encoding="latin1") as f:
        assert item.serialize() == f.read()
