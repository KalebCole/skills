#!/usr/bin/env bash
# Symlink every skill in skills/{engineering,productivity,personal}/ into
# ~/.hermes/skills/ and ~/.copilot/skills/.
#
# Skips in-progress/ and deprecated/.
# Fails loudly on name collisions unless --force is passed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

TARGETS=(
  "$HOME/.hermes/skills"
  "$HOME/.copilot/skills"
)

INSTALL_CATEGORIES=(engineering productivity personal)

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

collisions=0
installed=0
skipped_deprecated=0

for target in "${TARGETS[@]}"; do
  if [[ ! -d "$target" ]]; then
    echo "warning: $target does not exist, creating it" >&2
    mkdir -p "$target"
  fi
done

# Clean up symlinks pointing at deprecated/in-progress skills
for target in "${TARGETS[@]}"; do
  for link in "$target"/*; do
    [[ -L "$link" ]] || continue
    resolved="$(readlink "$link")"
    if [[ "$resolved" == *"/skills/deprecated/"* || "$resolved" == *"/skills/in-progress/"* ]]; then
      echo "cleanup: removing stale link $link → $resolved"
      rm "$link"
      ((skipped_deprecated++))
    fi
  done
done

# Install active skills
for category in "${INSTALL_CATEGORIES[@]}"; do
  cat_dir="$SKILLS_DIR/$category"
  [[ -d "$cat_dir" ]] || continue
  for skill_dir in "$cat_dir"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    skill_dir="${skill_dir%/}"

    for target in "${TARGETS[@]}"; do
      dest="$target/$skill_name"

      # Already correctly symlinked to this skill — idempotent, skip silently
      if [[ -L "$dest" && "$(readlink "$dest")" == "$skill_dir" ]]; then
        continue
      fi

      if [[ -e "$dest" || -L "$dest" ]]; then
        if [[ "$FORCE" -eq 1 ]]; then
          mv "$dest" "$dest.bak"
          echo "backup: $dest → $dest.bak"
        else
          echo "COLLISION: $dest already exists. Run with --force to back it up and overwrite." >&2
          ((collisions++))
          continue
        fi
      fi

      ln -s "$skill_dir" "$dest"
      echo "linked: $dest → $skill_dir"
      ((installed++))
    done
  done
done

echo ""
echo "summary: $installed link(s) installed, $skipped_deprecated stale link(s) cleaned"

if [[ "$collisions" -gt 0 ]]; then
  echo "$collisions collision(s) — re-run with --force to resolve" >&2
  exit 1
fi
