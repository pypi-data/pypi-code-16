# -*- coding: utf-8 -*-
"""
Settings para o LI-Tools
"""
from __future__ import print_function, unicode_literals, with_statement, nested_scopes


# Linha de comando para o prompt
################################
TERMINAL_CMD = "li"

# Configurações do Projeto
##########################
CONFIG_FILE = "li-config"
ENV_NAME = "LI_PROJECT_PATH"

STAGE_DB = "db-staging.awsli.com.br"
STAGE_PORT = 5432

LOCAL_DB = 'service.postgres.local'
LOCAL_PORT = 5432

PYPI_NAME = "li-aws-deploy"

DOCKER_PATH_VAR = '\$\{LI_PROJECT_PATH\}'

CHECK_VPN = True

# Configurações para Testes
# Se não for informado no parametro
# rodar o teste usando o programa pela prioridade abaixo
# Se não encontrar nenhum destes, usa o unittest padrão
TEST_PRIORITY = [
    'behave',
    'nose',
    'pytest'
]

# Lista de Aplicações do Projeto
################################

# A ordem dos branchs é da
# branch mais volátil até a de producao
# Ex: develop, master
APPLICATIONS = [
    ('li-docker', ['master']),
    ('LI-Api-Carrinho', ['development', 'staging', 'production']),
    ('LI-Api-Catalogo', ['development', 'staging', 'production']),
    ('LI-Api-Envio', ['development', 'staging', 'production']),
    ('LI-Api-Faturamento', ['development', 'staging', 'production']),
    ('li-api-integration', ['development', 'staging', 'production']),
    ('LI-Api-Marketplace', ['development', 'staging', 'production']),
    ('LI-Api-Pagador', ['development', 'staging', 'production']),
    ('LI-Api-Pedido', ['development', 'staging', 'production']),
    ('LI-Api-Plataforma', ['development', 'staging', 'production']),
    ('LI-Api-V2', ['development', 'staging', 'production']),
    ('LI-AppApi', ['development', 'staging', 'production']),
    ('LI-AppConciliacao', ['staging', 'production']),
    ('LI-AppConciliacao-V2', ['staging', 'production']),
    ('LI-AppLoja', ['development', 'staging', 'production']),
    ('LI-AppPainel', ['development', 'staging', 'production']),
    ('LI-Worker', ['development', 'staging', 'production']),
    ('li-api-pagamento', ['beta', 'master']),
    ('li-worker-pagamento', ['beta', 'master']),
    ('li-worker-integration', ['development', 'staging', 'production']),
    ('LI-Repo', ['master']),
    ('LI-ApiClient', ['master']),
    ('LI-Common', ['master']),
    ('LI-Api-Flask', ['master']),
    ('Li-Worker-Importacao', ['staging', 'production']),
    ('LI-AWS-Deploy', ['master']),
    ('LI-OpsWorks', ['staging', 'production']),
    ('LI-Standalone', ['staging', 'production']),
    ('LI-Pagador', ['master']),
    ('LI-Pagador-Deposito', ['master']),
    ('LI-Pagador-MercadoPago', ['master']),
    ('LI-Pagador-Paghiper', ['master']),
    ('LI-Pagador-Boleto', ['master']),
    ('LI-Pagador-PagSeguro', ['master']),
    ('LI-Pagador-Entrega', ['master']),
    ('LI-Pagador-PayPal', ['master']),
    ('LI-Pagador-PagarMe', ['master']),
    ('LI-Pagador-PayPal-Transparente', ['master']),
    ('LI-Pagador-MercadoPago-Transparente', ['master']),
    ('li_testing', ['master', 'release']),
    ('li-internal-services', ['master'])
]

# Lista as Livrarias padrões do Projeto
# Os nomes abaixo devem ser o mesmo que aparece no comando 'pip freeze'
# Qto mais livrarias na lista, mais lento o comando 'li list' vai ficar
LIBRARIES = [
    'li-repo'
]

# Aplicações que minificam arquivos durante o deploy
MINIFY_BEFORE = [
    'LI-AppLoja'
]

# Aplicações que sincronizam arquivos no S3 durante o deploy
SYNC_S3 = [
    'LI-AppLoja',
    'LI-AppPainel'
]

# Compressão de arquivos estáticos
##################################
baseDirStatic = ["static", "loja", "estrutura", "v1"]

# Arquivos JS para minificar num unico arquivo
jsSources = [
    ("js", "jquery-1.10.1.min.js"),
    ("js", "jquery-ui.js"),
    ("js", "bootstrap.min.js"),
    ("js", "css3-mediaqueries.js"),
    ("js", "jquery.flexslider-min.js"),
    ("js", "jquery.mask.min.js"),
    ("js", "modernizr.custom.17475.js"),
    ("js", "jquery.cookie.min.js"),
    ("js", "jquery.rwdImageMaps.min.js"),
    ("js", "main.js")
]

# Arquivos CSS para minificar num unico arquivo
cssSources = [
    ("css", "bootstrap.css"),
    ("css", "font-awesome.css"),
    ("css", "font-awesome-ie7.css"),
    ("css", "font-awesome-v4.css"),
    ("css", "flexslider.css"),
    ("css", "prettify.css"),
    ("css", "es-cus.css"),
    ("css", "style.css"),
    ("css", "cores.css")
]

# Arquivos JS para minificar individualmente
jsAlone = [
    ("js", "produto.js"),
    ("js", "carrinho.js"),
    ("js", "checkout.js")
]

# Arquivos CSS para minificar individualmente
cssAlone = [
    ("css", "tema-escuro.css"),
    ("css", "ie-fix.css")
]

# CONFIGURACAO PARA DOCKER
##########################
DOCKER_REPO_NAME = "LI-Docker"
DOCKERFILE_NAME = "Dockerfile_local"

# CONFIGURAÇÃO PARA VCS
#######################
VCS_NAME = "BitBucket"
VCS_BASE_URL = "https://bitbucket.org/lojaintegradateam/"


# CONFIGURACAO PARA AMAZON WEB SERVICES
#######################################
USE_AWS = True
S3_SYNC_CMD = "aws s3 sync static/ s3://lojaintegrada.cdn/{branch}/static/ --acl public-read"

# AWS EC2 CONTAINER SERVICE
###########################

# Caso o nome do container seja
# diferente do nome da aplicacao
# fazer o de/para aqui
USE_ECR = True
ECR_NAME = {
    'LI-AppPainel': 'app-painel-production',
    'LI-AppApi': 'li-api-v1',
    'LI-AppLoja': 'li-app-loja',
    'LI-AppConciliacao': 'li-app-conciliacao'
}


# CONFIGURACAO PARA SLACK
#########################
USE_SLACK = True
TEST_CHANNEL = "#teste_automacao"

# CONFIGURACAO PARA DATADOG
###########################
USE_DATADOG = False

# CONFIGURACAO PARA GRAFANA
###########################
USE_GRAFANA = True
GRAFANA_MSG_URL = "http://services-int.awsli.com.br:8086/write?db=msgs"

# DICIONARIO DE DADOS
#####################

CONFIG_DICT = {
    "project_path": None,
    "docker_compose_path": None
}

if USE_AWS:
    CONFIG_DICT['aws_key'] = None
    CONFIG_DICT['aws_secret'] = None
    CONFIG_DICT['aws_region'] = None
    CONFIG_DICT['aws_account'] = None

if USE_SLACK:
    CONFIG_DICT['slack_url'] = None
    CONFIG_DICT['slack_channel'] = None
    CONFIG_DICT['slack_icon'] = None
    CONFIG_DICT['slack_user'] = None

if USE_DATADOG:
    CONFIG_DICT['datadog_api_key'] = None
    CONFIG_DICT['datadog_app_key'] = None
