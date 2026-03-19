# tests/test_cliparser.py

from __future__ import annotations

import pytest

from password_engine.cli.cliparser import cli_parser


def test_cli_parser_parses_version_command_and_options():
    commands, overrides = cli_parser(
        [
            "--dev-mode",
            "--dry-run",
            "--build-config",
            "--log-level",
            "debug",
            "--console-level",
            "INFO",
            "--stderr-level",
            "40",
            "--file-log",
            "--console-log",
            "--stderr-log",
            "--db-host",
            "db.example",
            "--db-name",
            "mydb",
            "--db-user",
            "alice",
            "--db-password",
            "secret",
            "--db-port",
            "5433",
            "version",
            "--uppercase",
        ]
    )

    assert len(commands) == 1
    assert commands[0].name == "version"
    assert commands[0].options == {"uppercase": True}

    assert overrides.dev_mode is True
    assert overrides.dry_run is True
    assert overrides.build_config is True
    assert overrides.log_level == "debug"
    assert overrides.console_level == "INFO"
    assert overrides.stderr_level == "40"
    assert overrides.file_log is True
    assert overrides.console_log is True
    assert overrides.stderr_log is True
    assert overrides.db_host == "db.example"
    assert overrides.db_name == "mydb"
    assert overrides.db_user == "alice"
    assert overrides.db_password == "secret"
    assert overrides.db_port == 5433


def test_cli_parser_parses_negative_boolean_options():
    commands, overrides = cli_parser(
        [
            "--no-dev-mode",
            "--no-dry-run",
            "--no-build-config",
            "--no-file-log",
            "--no-console-log",
            "--no-stderr-log",
            "version",
        ]
    )

    assert len(commands) == 1
    assert commands[0].name == "version"
    assert commands[0].options == {"uppercase": False}

    assert overrides.dev_mode is False
    assert overrides.dry_run is False
    assert overrides.build_config is False
    assert overrides.file_log is False
    assert overrides.console_log is False
    assert overrides.stderr_log is False


def test_cli_parser_returns_no_commands_when_no_subcommand():
    commands, overrides = cli_parser([])

    assert commands == ()
    assert overrides.dev_mode is None
    assert overrides.log_level is None
    assert overrides.db_port is None


def test_cli_parser_rejects_unknown_command():
    with pytest.raises(SystemExit) as exc_info:
        cli_parser(["does-not-exist"])

    assert exc_info.value.code == 2
