from importlib.metadata import version

from pytest_bdd import scenario, then, when

import volsegtools


@scenario("library/library.feature", "Retrieving the library version")
def test_version() -> None:
    pass


@when("I retrieve the library version", target_fixture="library_version")
def retrieve_version() -> str:
    return volsegtools.__version__


@then("the returned version matches the installed package version")
def check_version(library_version: str) -> None:
    assert library_version == version("volsegtools")
