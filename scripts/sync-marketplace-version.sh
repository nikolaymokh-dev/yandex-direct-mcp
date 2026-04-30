#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="${HOME}/Projects/yandex-direct-mcp-plugin"
MARKETPLACE_DIR="${HOME}/Projects/plugin-marketplace"
PLUGIN_NAME="yandex-direct"

PLUGIN_JSON="${PLUGIN_DIR}/.claude-plugin/plugin.json"
MARKETPLACE_JSON="${MARKETPLACE_DIR}/.claude-plugin/marketplace.json"

command -v jq >/dev/null || { echo "error: jq is required" >&2; exit 1; }
[[ -f "$PLUGIN_JSON" ]] || { echo "error: $PLUGIN_JSON not found" >&2; exit 1; }
[[ -f "$MARKETPLACE_JSON" ]] || { echo "error: $MARKETPLACE_JSON not found" >&2; exit 1; }

new_version=$(jq -r '.version' "$PLUGIN_JSON")
current_version=$(jq -r --arg name "$PLUGIN_NAME" \
  '.plugins[] | select(.name == $name) | .version' "$MARKETPLACE_JSON")

if [[ -z "$current_version" || "$current_version" == "null" ]]; then
  echo "error: plugin '$PLUGIN_NAME' not found in marketplace.json" >&2
  exit 1
fi

if [[ "$current_version" == "$new_version" ]] \
   && git -C "$MARKETPLACE_DIR" diff --quiet -- .claude-plugin/marketplace.json \
   && git -C "$MARKETPLACE_DIR" diff --cached --quiet -- .claude-plugin/marketplace.json; then
  echo "Already at ${new_version}, nothing to do"
  exit 0
fi

echo "Bumping marketplace ${PLUGIN_NAME}: ${current_version} → ${new_version}"

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
jq --arg name "$PLUGIN_NAME" --arg v "$new_version" \
  '(.plugins[] | select(.name == $name) | .version) = $v' \
  "$MARKETPLACE_JSON" > "$tmp"
mv "$tmp" "$MARKETPLACE_JSON"
trap - EXIT

git -C "$MARKETPLACE_DIR" pull --rebase origin main
git -C "$MARKETPLACE_DIR" add .claude-plugin/marketplace.json
git -C "$MARKETPLACE_DIR" commit -m "chore: bump ${PLUGIN_NAME} plugin to ${new_version}"
git -C "$MARKETPLACE_DIR" push origin main

echo "Done."
