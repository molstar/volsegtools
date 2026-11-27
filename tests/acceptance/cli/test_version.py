from importlib.metadata import version

from pytest_bdd import scenario, then, when
from typer.testing import CliRunner

from volsegtools._cli import main_app


@scenario("cli/cli.feature", "Displaying the application version")
def test_version() -> None:
    pass


@when("I execute the version command", target_fixture="result")
def execute_version_command():
    return CliRunner().invoke(main_app, ["version"])


@then("the current application version is printed")
def check_version(result) -> None:
    assert result.stdout.strip() == f"Version: {version('volsegtools')}"


@then("the command exits successfully")
def check_exit_code(result) -> None:
    assert result.exit_code == 0
