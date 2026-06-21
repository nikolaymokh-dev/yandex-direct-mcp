# yandex-direct-mcp

Hardened форк [axisrow/yandex-direct-mcp-plugin](https://github.com/axisrow/yandex-direct-mcp-plugin). Управление Яндекс.Директом из MCP-клиента (Claude Code, Cursor и другие). **Только чтение по умолчанию** — запись включается явно через `YANDEX_DIRECT_ENABLE_WRITES=true`. OAuth реализован пакетом `direct-cli` (бинарь `direct`); каждый пользователь авторизуется под своим Яндекс-аккаунтом.

---

## Профили и поверхность инструментов

| Профиль | Как активируется | Что включено | Инструментов |
|---|---|---|---|
| **analytics** (по умолчанию) | — | Отчёты, статистика, прогноз, Wordstat, словари, изменения (только чтение) | ~26 |
| **campaign-editor** | `YANDEX_DIRECT_ENABLE_WRITES=true` | Управление кампаниями, группами, объявлениями, ставками (чтение + запись) | ~36 |
| Финансы | `YANDEX_DIRECT_ENABLE_FINANCE=true` **вместе** с writes | Пополнение счёта, счета, переводы (`v4account_deposit` / `invoice` / `transfer_money`) | +3 |
| **full** | `YANDEX_DIRECT_TOOL_PROFILE=full` | Все 146 инструментов | 146 |

### Переменные окружения

| Переменная | Назначение |
|---|---|
| `YANDEX_DIRECT_ENABLE_WRITES` | `true` → активирует профиль `campaign-editor`. По умолчанию не установлена (только чтение). |
| `YANDEX_DIRECT_ENABLE_FINANCE` | `true` → включает финансовые инструменты. Работает **только вместе** с `ENABLE_WRITES`; на профиле `analytics` не даёт эффекта. |
| `YANDEX_DIRECT_TOOL_PROFILE` | Явный выбор профиля: `analytics` \| `core` \| `campaign-editor` \| `full`. Переопределяет логику ENABLE_WRITES. |
| `YANDEX_DIRECT_ENABLED_GROUPS` | Allow-list групп (через запятую): `campaigns`, `ads`, `read`, `mutate`, `analytics`, … |
| `YANDEX_DIRECT_DISABLED_GROUPS` | Убрать группы из активной поверхности (не расширяет до full — safe-by-default). |
| `YANDEX_DIRECT_ENABLED_TOOLS` | Allow-list конкретных инструментов (через запятую). |
| `YANDEX_DIRECT_DISABLED_TOOLS` | Убрать конкретные инструменты из активной поверхности. |

> **Важно:** `DISABLED_*` переменные уточняют активную поверхность, но не расширяют её до полного набора. Если одновременно не указаны `ENABLED_*`, не выставлен явный `TOOL_PROFILE` и не установлен `ENABLE_WRITES=true` — сервер стартует в профиле `analytics` (только чтение).

> **Приоритет:** `YANDEX_DIRECT_ENABLE_WRITES` игнорируется, если задан `YANDEX_DIRECT_TOOL_PROFILE` или любая из `YANDEX_DIRECT_ENABLED_GROUPS`/`YANDEX_DIRECT_ENABLED_TOOLS` — явный профиль или allow-list имеют приоритет.

---

## Установка

### Claude Code (рекомендуемый способ — uvx)

```sh
claude mcp add yandex-direct \
  -- uvx --from git+https://github.com/nikolaymokh-dev/yandex-direct-mcp@v0.1.0 yandex-direct-mcp
```

Чтобы включить запись:

```sh
claude mcp add yandex-direct \
  --env YANDEX_DIRECT_ENABLE_WRITES=true \
  -- uvx --from git+https://github.com/nikolaymokh-dev/yandex-direct-mcp@v0.1.0 yandex-direct-mcp
```

### `.claude.json` / Cursor / другие MCP-клиенты

```json
{
  "mcpServers": {
    "yandex-direct": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/nikolaymokh-dev/yandex-direct-mcp@v0.1.0",
        "yandex-direct-mcp"
      ],
      "env": {
        "YANDEX_DIRECT_ENABLE_WRITES": "true"
      }
    }
  }
}
```

Поле `"env"` не обязательно — без него сервер запускается в read-only (`analytics`) режиме.

### Запуск standalone (без MCP-клиента, для проверки)

```sh
uvx --from git+https://github.com/nikolaymokh-dev/yandex-direct-mcp@v0.1.0 yandex-direct-mcp
```

Запускает stdio-сервер напрямую (для теста установки; обычно сервер запускает MCP-клиент).

---

## Первый вход (OAuth / PKCE)

После установки и запуска MCP-сервера вызовите инструмент `auth_login`:

```
mcp__yandex_direct__auth_login()
```

Сервер напечатает URL. Откройте его в браузере и авторизуйтесь в **своём** Яндекс-аккаунте. PKCE-поток реализован пакетом `direct-cli`; токен сохраняется локально в `~/.direct-cli/auth.json` (права 0600).

> **Не используйте** `auth_setup(code=...)` на общих машинах — код авторизации будет виден в `ps` и системных логах.

---

## Включение управления кампаниями и финансов

Запись (управление кампаниями, группами, объявлениями, ставками):

```sh
# В ~/.claude/settings.json
{
  "env": {
    "YANDEX_DIRECT_ENABLE_WRITES": "true"
  }
}
```

Финансовые инструменты (пополнение, счета, переводы) — отдельное осознанное решение:

```sh
{
  "env": {
    "YANDEX_DIRECT_ENABLE_WRITES": "true",
    "YANDEX_DIRECT_ENABLE_FINANCE": "true"
  }
}
```

> ⚠ Финансовые операции работают с **реальными деньгами**. Включайте только в окружениях с явными правами на финансовые транзакции.

---

## (Опционально) Запуск как Claude Code плагин

Если репозиторий клонирован локально, плагин запускается через `hooks/run-server.sh`:

```jsonc
// .mcp.json (пример для Claude Code plugin channel)
{
  "mcpServers": {
    "yandex-direct-mcp": {
      "command": "bash",
      "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/run-server.sh"]
    }
  }
}
```

Детали bootstrap и troubleshooting — в [`hooks/setup.sh`](hooks/setup.sh) и CLAUDE.md.

---

## Документация

- **Настройка доступа к API** → [docs/SETUP.md](docs/SETUP.md)
- **Модель угроз и безопасность** → [docs/SECURITY.md](docs/SECURITY.md)
- **Синхронизация с upstream** → [docs/SYNC.md](docs/SYNC.md)

---

## Лицензия

MIT — форк [axisrow/yandex-direct-mcp-plugin](https://github.com/axisrow/yandex-direct-mcp-plugin), см. [NOTICE](NOTICE).
