# Contributing

Personal skills repo. PRs from outside are welcome but the bar is "is this useful to Kaleb."

## Adding a skill

1. Pick a category folder under `skills/`:
   - `engineering/` — code, tooling, development workflows
   - `productivity/` — generic productivity patterns (no personal accounts/tokens required)
   - `personal/` — skills tied to specific accounts, vaults, or identity (YNAB, Todoist, etc.)
   - `in-progress/` — half-built; **excluded from install**
   - `deprecated/` — kept for reference; **excluded from install**
2. Create `skills/<category>/<skill-name>/SKILL.md` with YAML frontmatter:
   ```md
   ---
   name: skill-name
   description: One-line description that triggers loading.
   ---
   ```
3. Run `python3 scripts/generate-readme.py` to refresh the catalog table.
4. Commit. CI will fail if the README is out of sync.

## Installing

```bash
./scripts/install.sh
```

Symlinks every skill in `skills/` (except `in-progress/` and `deprecated/`) into:

- `~/.hermes/skills/`
- `~/.copilot/skills/`

If a target already exists in either directory, install fails. Use `--force` to overwrite (existing entries are renamed to `<name>.bak`).

## Removing a skill

Move the folder to `deprecated/` rather than deleting. Re-run install — symlinks for deprecated skills get cleaned up automatically.
