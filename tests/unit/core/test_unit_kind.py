import pydantic
import pytest

import volsegtools as vst


@pytest.mark.parametrize(
    "micrometers, angstroms",
    [
        (0, 0),
        (1, 10_000),
        (0.123, 1_230),
    ],
)
def test_to_angstroms(micrometers, angstroms):
    assert vst.to_angstrom(micrometers) == angstroms


@pytest.mark.parametrize(
    "micrometers, angstroms",
    [
        (0, 0),
        (1, 10_000),
        (0.123, 1_230),
    ],
)
def test_to_micrometers(micrometers, angstroms):
    assert vst.to_micrometer(angstroms) == micrometers


@pytest.mark.parametrize("micrometers", [0, 1, 0.123])
def test_to_angstroms_and_back(micrometers):
    assert vst.to_micrometer(vst.to_angstrom(micrometers)) == micrometers


@pytest.mark.parametrize("angstroms", [0, 10_000, 1_2300])
def test_to_micrometers_and_back(angstroms):
    assert vst.to_angstrom(vst.to_micrometer(angstroms)) == angstroms


@pytest.mark.parametrize(
    "string, kind",
    [
        ("um", vst.UnitKind.MICRO_METER),
        ("μm", vst.UnitKind.MICRO_METER),
        ("micro", vst.UnitKind.MICRO_METER),
        ("angstrom", vst.UnitKind.ANGSTROM),
        ("Å", vst.UnitKind.ANGSTROM),
        ("wrong", vst.UnitKind.UNKNOWN),
    ],
)
def test_unit_from_str(string, kind):
    assert vst.unit_from_str(string) == kind


@pytest.mark.parametrize(
    "kind, serialized",
    [
        (vst.UnitKind.UNKNOWN, "unknown"),
        (vst.UnitKind.MICRO_METER, "micro_meter"),
        (vst.UnitKind.ANGSTROM, "angstrom"),
        (vst.UnitKind.NANO_METER, "nano_meter"),
    ],
)
def test_serialization(kind, serialized):
    adapter = pydantic.TypeAdapter(vst.Unit)
    assert adapter.dump_python(kind, mode="python") == serialized
