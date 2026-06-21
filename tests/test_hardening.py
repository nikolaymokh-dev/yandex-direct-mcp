"""Hardening tests — Task 2: uvx console-script entry point."""


def test_run_entry_point_is_callable():
    from server.main import run

    assert callable(run)
