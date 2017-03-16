# coding=utf-8
from os import path
import codecs

from telecom_invoice.models import Register

FIXTURES = path.join(path.dirname(__file__), "fixtures")


def test_register():
    register = Register()
    # 1 CNPJ ou CPF | len 14 | 1-14 | int
    register.registration.value = 47827332000108
    # 2 IE | len 14 | 15-28 | str
    register.state_subscription.value = "492175108116"
    # 3 Razão Social | len 35 | 29-63 | str
    register.legal_name.value = "Agro  Safra Ind e Com de Adubos Ltd"
    # 4 Logradouro | len 45 | 64-108 | str
    register.street.value = "R Frei Egidio Laurent"
    # 5 Número | len 5 | 109-113 | int
    register.number.value = 179
    # 7 CEP | len 8 | 129-136 | int
    register.zip_code.value = 6298020
    # 8 Bairro | len 15 | 137-151 | str
    register.neighborhood.value = u"Vila dos Remédi"
    # 9 Município | len 30 | 152-181 | str
    register.city.value = "OSASCO"
    # 10 UF | len 2 | 182-183 | str
    register.state_code.value = "SP"
    # 11 Telefone de contato | len 12 | 184-195 | int
    register.phone.value = 1136875766
    # 12 Código de Identificação do consumidor ou assinante | len 12 | 196-207 | str
    register.client_code.value = "1079"
    # 13 Número do terminal telefônico ou Número de conta do consumo | len 12 | 208-219 | str
    register.contract_code.value = "1136875766"
    # 14 UF de habilitação do terminal telefônico | len 2 | 220-221 | str
    register.contract_state.value = "SP"

    with codecs.open(path.join(FIXTURES, "SP0011403ND.001"), "r", encoding="latin1") as f:
        assert register.serialize() == f.read()
