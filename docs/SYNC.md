# Синхронизация с upstream

Форк отслеживает [axisrow/yandex-direct-mcp-plugin](https://github.com/axisrow/yandex-direct-mcp-plugin) как remote `upstream`.

## Процедура ре-синка

```bash
git fetch upstream

# ОБЯЗАТЕЛЬНО: прочитать каждый коммит перед мерджем.
# Это сторонний код с доступом к рекламным бюджетам — не мерджить вслепую.
git log --oneline HEAD..upstream/main

git merge upstream/main
# При конфликтах: переприменить харденинг (config_from_env, entry-point, default-surface).

# Отзеркалить server/ → plugins/yandex-direct/server/
# (diff -q должен быть чистым после синка)
bash scripts/sync-codex-bundle.sh

uv lock && uv sync --extra dev

# Прогнать suite
uv run pytest -q -m "not integration and not live_safe and not live_unsafe"

# Проверить, что дефолтный профиль всё ещё analytics
python -c "
from server.config import config_from_env
cfg = config_from_env({})
print('default enabled_tool_names count:', len(cfg.enabled_tool_names()))
"

# Убедиться, что bundle не разъехался
# (test_codex_bundle_sync.py должен быть зелёным)

# При необходимости — bump тега
# scripts/update-version.sh X.Y.Z
```

## Обязательные инварианты после синка

1. **Дефолтный профиль = `analytics`** (только чтение). `config_from_env({})` должен возвращать ~26 инструментов.
2. **Bundle отзеркален**: `server/` и `plugins/yandex-direct/server/` байт-идентичны (тест `test_codex_bundle_mirrors_repo_server_tree`).
3. **Вся suite зелёная**: `pytest -q -m "not integration and not live_safe and not live_unsafe"`.
4. **Харденинг на месте**: `server/main.py` содержит `apply_tool_surface`, `config_from_env`, `env_config_warnings` (тест `test_entrypoint_wires_tool_surface_config`).

## Что никогда не делать

- Не мерджить upstream вслепую (`git merge upstream/main` без предварительного `git log --oneline HEAD..upstream/main`).
- Не убирать `YANDEX_DIRECT_ENABLE_WRITES` / `config_from_env` из `server/config.py` — это и есть харденинг.
- Не менять дефолтный профиль с `analytics` на `full` без явного решения и обновления этой документации.
