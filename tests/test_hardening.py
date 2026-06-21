"""Hardening tests — Task 2: uvx console-script entry point."""


def test_run_entry_point_is_callable():
    from server.main import run

    assert callable(run)


from server.config import PROFILES, config_from_env


def _surface(cfg):
    return (
        cfg.default_enabled,
        frozenset(cfg.enabled_groups),
        frozenset(cfg.disabled_groups),
        frozenset(cfg.enabled_tools),
        frozenset(cfg.disabled_tools),
    )


def test_empty_env_defaults_to_analytics():
    assert _surface(config_from_env({})) == _surface(PROFILES["analytics"])


def test_enable_writes_selects_campaign_editor():
    cfg = config_from_env({"YANDEX_DIRECT_ENABLE_WRITES": "true"})
    assert _surface(cfg) == _surface(PROFILES["campaign-editor"])


def test_explicit_profile_still_respected():
    cfg = config_from_env({"YANDEX_DIRECT_TOOL_PROFILE": "full"})
    assert cfg.default_enabled is True


def test_enable_finance_reenables_financial_group():
    cfg = config_from_env(
        {"YANDEX_DIRECT_ENABLE_WRITES": "true", "YANDEX_DIRECT_ENABLE_FINANCE": "true"}
    )
    assert "financial" in cfg.enabled_groups
    assert "financial" not in cfg.disabled_groups


def test_explicit_groups_branch_preserved():
    cfg = config_from_env({"YANDEX_DIRECT_ENABLED_GROUPS": "analytics"})
    assert cfg.default_enabled is False
