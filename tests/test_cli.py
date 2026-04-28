from __future__ import annotations

import pytest

from glassbox.cli import main


def test_cli_help(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "Local flight recorder" in captured.out


def test_doctor_outputs_diagnostics(capsys) -> None:
    result = main(["doctor"])

    captured = capsys.readouterr()

    assert result == 0
    assert "Glassbox diagnostics" in captured.out
    assert "python:" in captured.out
