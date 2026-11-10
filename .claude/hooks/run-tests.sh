#!/usr/bin/env bash
# PostToolUse: po Edit/Write uruchamia testy serwisu, którego dotyczy zmieniony plik.
# Exit 2 = testy nie przechodzą -> stderr wraca do Claude jako feedback.

f=$(jq -r '.tool_input.file_path')        # JSON zdarzenia przychodzi na stdin

case "$f" in */services/api/*) s=api ;; */services/ml/*) s=ml ;; *) exit 0 ;; esac

cd "$CLAUDE_PROJECT_DIR/services/$s" && uv run pytest -q -x >&2 || exit 2
