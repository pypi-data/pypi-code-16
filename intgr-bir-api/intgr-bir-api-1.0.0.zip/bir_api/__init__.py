# -*- coding: utf-8 -*-

VERSION = '1.0.0'

NAMESPACES = {
    'bir': 'http://CIS/BIR/PUBL/2014/07',
    'pb': 'http://CIS/BIR/2014/07'
}

DETAILED_REPORT_NAMES_MAP = {
    '6': 'PublDaneRaportPrawna',
    '1': 'PublDaneRaportDzialalnoscFizycznejCeidg',
    '2': 'PublDaneRaportDzialalnoscFizycznejRolnicza',
    '3': 'PublDaneRaportDzialalnoscFizycznejPozostala',
    '4': 'PublDaneRaportDzialalnoscFizycznejWKrupgn'
}

COMPANY_FIELD_MAP = {
    ('Nazwa', 'name'),
    ('Nip', 'vat_no'),
    ('Regon', 'regon'),
    ('Krs', 'krs'),
    ('Ulica', 'street'),
    ('KodPocztowy', 'zip_code'),
    ('Miejscowosc', 'city'),
    ('Wojewodztwo', 'voivodeship'),
    ('Powiat', 'county'),
    ('Gmina', 'community'),
    ('Typ', 'type'),
}

