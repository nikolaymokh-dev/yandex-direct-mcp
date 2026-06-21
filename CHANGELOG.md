# Changelog

Изменения этого форка относительно upstream
[axisrow/yandex-direct-mcp-plugin](https://github.com/axisrow/yandex-direct-mcp-plugin).
Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

> **О версии.** Метаданные пакета (`pyproject.toml` `version`) намеренно оставлены
> равными версии upstream (`0.3.3`), чтобы не ломать встроенную в репозиторий
> систему сверки версий (`scripts/runtime-pins.env`, `tests/test_pins_consistency.py`,
> манифесты плагина). Релизы самого форка отслеживаются git-тегами, начиная с
> **`v0.1.0`** — именно по тегу партнёры ставят сервер
> (`uvx --from git+...@v0.1.0`). Этот `v0.1.0` основан на upstream `0.3.3`.

## [v0.1.0] — 2026-06-21 (hardened fork, на базе upstream 0.3.3)

Базовый форк взят с upstream-коммита `8f7bc01`-предшественника (146 инструментов).
Ниже — всё, что добавлено/изменено в форке поверх оригинала.

### Безопасность (главное, ради чего форк)

- **Read-only по умолчанию.** Без флагов сервер отдаёт профиль `analytics`
  (~26 инструментов: отчёты, статистика, прогноз, Wordstat, словари, проверка
  изменений) — нельзя случайно изменить кампанию или потратить бюджет. Раньше по
  умолчанию открывались все 146 инструментов (`full`).
- **Управление — по флагу.** `YANDEX_DIRECT_ENABLE_WRITES=true` включает профиль
  `campaign-editor` (~36 инструментов: кампании, группы, объявления, ставки).
- **Финансы — отдельно и только вместе с записью.** `YANDEX_DIRECT_ENABLE_FINANCE=true`
  возвращает финансовые инструменты (`v4account_deposit`/`invoice`/`transfer_money`)
  только когда активен write-профиль; на read-only-дефолте флаг — no-op (деньги
  не утекут без явного включения записи). Финансы дополнительно защищены
  upstream-механикой `dry_run`/`sandbox`.
- **`DISABLED_*` уточняют, а не расширяют.** `YANDEX_DIRECT_DISABLED_GROUPS`/
  `DISABLED_TOOLS` без явного профиля теперь применяются поверх read-only-базы и
  НЕ открывают полную поверхность (safe-by-default). Для всех 146 инструментов —
  явный `YANDEX_DIRECT_TOOL_PROFILE=full`.

### Дистрибуция и сопровождение

- **uvx-установка.** Добавлена console-script точка входа `server.main:run` +
  `[project.scripts]`, поэтому сервер ставится одной командой
  `uvx --from git+https://github.com/nikolaymokh-dev/yandex-direct-mcp@v0.1.0 yandex-direct-mcp`
  в любом MCP-клиенте. Исходный путь Claude Code плагина (`hooks/run-server.sh`,
  `.mcp.json`) продолжает работать.
- **Запинённое дерево зависимостей** (`uv.lock`) — поверх уже точечно
  запинённых upstream `mcp==1.23.3` / `direct-cli==0.4.3`, фиксирует и транзитивные
  пакеты (`tapi-wrapper2` и т.д.).
- Документация: [docs/SETUP.md](docs/SETUP.md) (OAuth через `direct-cli`),
  [docs/SECURITY.md](docs/SECURITY.md) (модель угроз), [docs/SYNC.md](docs/SYNC.md)
  (безопасный ре-синк с upstream), [NOTICE](NOTICE) (атрибуция MIT).
- Тесты безопасности: дефолт=analytics, ENABLE_WRITES→campaign-editor,
  ENABLE_FINANCE-только-с-writes, DISABLED_*-не-расширяет, subprocess-проверка
  read-only поверхности сервера.

### Отложено (v0.2)

- Свой Yandex OAuth-app (форк `direct-cli` со своим `client_id`), чтобы экран
  согласия показывал твоё приложение. Сейчас OAuth/PKCE обеспечивает штатный
  `direct-cli`; токен выписывается на аккаунт пользователя и хранится локально
  (`~/.direct-cli/auth.json`, 0600).

### Без изменений

- Набор и поведение самих инструментов Яндекс.Директа (когда включены) — как в upstream.
- Транспорт строго через `direct-cli` (MCP не ходит в API напрямую) — как в upstream.

[v0.1.0]: https://github.com/nikolaymokh-dev/yandex-direct-mcp/releases/tag/v0.1.0
