# coding: utf-8

RESOURCE_MAPPING = {
    'empresas': {
        'resource': 'empresas',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa': {
        'resource': 'empresas/{empresaId}',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_certificado_digital': {
        'resource': 'empresas/{empresaId}/certificadoDigital',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_logo': {
        'resource': 'empresas/{empresaId}/logo',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfes': {
        'resource': 'empresas/{empresaId}/nfes',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe': {
        'resource': 'empresas/{empresaId}/nfes/{nfeId}',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe_pdf': {
        'resource': 'empresas/{empresaId}/nfes/{nfeId}/pdf',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe_xml': {
        'resource': 'empresas/{empresaId}/nfes/{nfeId}/xml',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe_externo': {
        'resource': 'empresas/{empresaId}/nfes/porIdExterno/{idExterno}',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe_externo_pdf': {
        'resource': 'empresas/{empresaId}/nfes/porIdExterno/{idExterno}/pdf',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
    'empresa_nfe_externo_xml': {
        'resource': 'empresas/{empresaId}/nfes/porIdExterno/{idExterno}/xml',
        'docs': 'http://app.enotasgw.com.br/docs'
    },
}
