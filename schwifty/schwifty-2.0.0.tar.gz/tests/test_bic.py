import pytest

from schwifty import BIC


def test_bic():
    bic = BIC('GENODEM1GLS')
    assert bic.formatted == 'GENO DE M1 GLS'
    assert bic.validate()


def test_bic_allow_invalid():
    bic = BIC('GENODXM1GLS', allow_invalid=True)
    assert bic
    assert bic.country_code == 'DX'
    with pytest.raises(ValueError):
        bic.validate()


def test_bic_no_branch_code():
    bic = BIC('GENODEM1')
    assert bic.branch_code is None
    assert bic.formatted == 'GENO DE M1'


def test_country_bank_code():
    assert BIC('ABNAJPJTXXX').country_bank_code is None
    assert BIC('GENODEM1GLS').country_bank_code == '43060967'


def test_bic_properties():
    bic = BIC('GENODEM1GLS')
    assert bic.length == 11
    assert bic.bank_code == 'GENO'
    assert bic.branch_code == 'GLS'
    assert bic.country_code == 'DE'
    assert bic.location_code == 'M1'
    assert bic.country_bank_code == '43060967'
    assert bic.exists
    assert bic.type == 'passive'


@pytest.mark.parametrize('code,type', [
    ('GENODEM0GLS', 'testing'),
    ('GENODEM1GLS', 'passive'),
    ('GENODEM2GLS', 'reverse billing'),
    ('GENODEMMGLS', 'default')
])
def test_bic_type(code, type):
    bic = BIC(code)
    assert bic.type == type


@pytest.mark.parametrize('code', [
    'AAAA',             # Too short
    'AAAADEM1GLSX',     # Too long
    '12ABDEM1GLS',      # Wrong structure in banc-id
    'GENOD1M1GLS',      # Wrong structure in country-code
    'GENOXXM1GLS',      # Wrong country-code
])
def test_invalid_bic(code):
    with pytest.raises(ValueError):
        BIC(code)


def test_bic_from_bank_code():
    bic = BIC.from_bank_code('DE', '43060967')
    assert bic.compact == 'GENODEM1GLS'


def test_bic_from_unknown_bank_code():
    with pytest.raises(ValueError):
        BIC.from_bank_code('PO', '12345678')


def test_bic_is_from_primary_bank_code():
    bic = BIC.from_bank_code('DE', '20070024')
    assert bic.compact == 'DEUTDEDBHAM'


def test_magic_methods():
    bic = BIC('GENODEM1GLS')
    assert bic == 'GENODEM1GLS'
    assert bic == BIC('GENODEM1GLS')
    assert bic != BIC('GENODEMMXXX')
    assert bic != 12345
    assert bic < 'GENODEM1GLT'

    assert str(bic) == 'GENODEM1GLS'
    assert repr(bic) == '<BIC=GENODEM1GLS>'
