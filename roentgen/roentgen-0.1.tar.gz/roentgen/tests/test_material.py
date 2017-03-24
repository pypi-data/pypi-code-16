import pytest
from roentgen.material import MassAttenuationCoefficient, Material, Compound
import roentgen
import numpy as np
import astropy.units as u

@pytest.fixture(params=roentgen.material_list.keys())
def mass_atten(request):
    return MassAttenuationCoefficient(request.param)

def test_mass_atten(mass_atten):
    # check that all materials can load a MassAttenuationCoefficient object
    assert isinstance(mass_atten, MassAttenuationCoefficient)


def test_returns_quantity(mass_atten):
    assert isinstance(mass_atten.func(1 * u.keV), u.Quantity)


def test_number_of_energies(mass_atten):
    energy = u.Quantity(np.arange(1, 1000), 'keV')
    atten = mass_atten.func(energy)
    assert len(energy) == len(atten)


@pytest.fixture(params=roentgen.material_list.keys())
def material(request):
    return Material(request.param, 500 * u.micron)


@pytest.fixture(params=roentgen.material_list.keys())
def material_dict(request):
    return roentgen.material_list[request.param]


def test_has_default_density(material_dict):
    # test if materials have a default density provided
    assert material_dict.get('density', 'None') != None

def test_material(material):
    assert isinstance(material, Material)


def test_twomaterials_to_compound(material):
    # check that adding two materials returns a compound
    assert isinstance(material + Material('si', 500 * u.micron), Compound)


def test_threematerials_to_compound(material):
    # check that adding three materials returns a compound
    assert isinstance(Material('si', 500 * u.micron) +
                      Material('ge', 500 * u.micron) +
                      Material('cdte', 100 * u.micron), Compound)


@pytest.fixture(params=roentgen.material_list.keys())
def thick_material(request):
    return Material(request.param, 500 * u.Mm)


def test_opaque(thick_material):
    # check that extremely large amounts of material mean no transmission
    assert thick_material.transmission(1 * u.keV) == 0


@pytest.fixture(params=roentgen.material_list.keys())
def thin_material(request):
    return Material(request.param, 1e-6 * u.pm)


def test_transparent(thin_material):
    # check that extremely large amounts of material mean no transmission
    assert thin_material.transmission(1 * u.keV) > 0.9

