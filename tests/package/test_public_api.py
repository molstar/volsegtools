import inspect

import pytest

import volsegtools as vst

# The whole purpose of this test is to check that all symbols that we percieve
# as public are indeed public **and** that they have their module set to the
# highest level package -- volsegtools.


@pytest.mark.parametrize("symbol", vst.__all__)
def test_public_objects_report_public_module(symbol):
    obj = getattr(vst, symbol)
    if inspect.isclass(obj) or inspect.isfunction(obj):
        assert obj.__module__ == "volsegtools", symbol


@pytest.mark.parametrize("symbol", vst.abc.__all__)
def test_public_objects_report_public_module_abc(symbol):
    obj = getattr(vst.abc, symbol)
    if inspect.isclass(obj) or inspect.isfunction(obj):
        assert obj.__module__ == "volsegtools.abc", symbol
