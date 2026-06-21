"""Hardening tests — entry point + tool-surface defaults/flags.

Covers:
* uvx console-script entry point (callable ``run``).
* Safe-by-default contract: no env vars → analytics read-only surface.
* ENABLE_WRITES opt-in: selects campaign-editor profile.
* ENABLE_FINANCE gate: finance must NOT open without a write-capable profile.
* DISABLED_*-only refinement stays on the read-only analytics base.
"""


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


def test_enable_finance_without_writes_is_noop():
    cfg = config_from_env({"YANDEX_DIRECT_ENABLE_FINANCE": "true"})
    # analytics default is read-only; finance must NOT be enabled without writes
    assert _surface(cfg) == _surface(PROFILES["analytics"])
    assert "financial" not in cfg.enabled_groups


def test_disabled_groups_only_uses_hardened_default_not_full():
    # Safe-by-default: DISABLED_* refine the active surface; they do NOT imply the
    # full surface. Without a profile/ENABLED_*, the base stays read-only (analytics).
    cfg = config_from_env({"YANDEX_DIRECT_DISABLED_GROUPS": "destructive"})
    assert cfg.default_enabled is False
