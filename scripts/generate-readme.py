#!/usr/bin/env python3
"""
Generate the skills catalog table in README.md.

Reads YAML frontmatter (name + description) from every SKILL.md under skills/
and writes a grouped catalog between marker comments in README.md.

Markers:
    <!-- CATALOG:START -->
    ...generated...
    <!-- CATALOG:END -->

Run manually after adding/removing skills. CI verifies the file is up to date.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
README = REPO_ROOT / "README.md"

CATEGORY_ORDER = ["engineering", "productivity", "personal", "in-progress", "deprecated"]
CATEGORY_TITLES = {
    "engineering": "Engineering",
    "productivity": "Productivity",
    "personal": "Personal",
    "in-progress": "In Progress",
    "deprecated": "Deprecated",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)


def parse_skill(skill_md: Path) -> dict | None:
    text = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        print(f"warning: no frontmatter in {skill_md}", file=sys.stderr)
        return None
    fm = m.group(1)
    name_m = NAME_RE.search(fm)
    desc_m = DESC_RE.search(fm)
    if not name_m or not desc_m:
        print(f"warning: missing name/description in {skill_md}", file=sys.stderr)
        return None
    return {"name": name_m.group(1).strip(), "description": desc_m.group(1).strip()}


def collect() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {c: [] for c in CATEGORY_ORDER}
    for category in CATEGORY_ORDER:
        cat_dir = SKILLS_DIR / category
        if not cat_dir.exists():
            continue
        for skill_dir in sorted(cat_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            parsed = parse_skill(skill_md)
            if parsed:
                out[category].append(parsed)
    return out


def render(skills_by_cat: dict[str, list[dict]]) -> str:
    lines: list[str] = []
    total = sum(len(v) for v in skills_by_cat.values())
    lines.append(f"_{total} skill(s) total._\n")
    for category in CATEGORY_ORDER:
        skills = skills_by_cat[category]
        if not skills:
            continue
        lines.append(f"### {CATEGORY_TITLES[category]}\n")
        for s in skills:
            lines.append(f"- **`{s['name']}`** — {s['description']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_readme(catalog: str) -> bool:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(<!-- CATALOG:START -->)(.*?)(<!-- CATALOG:END -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        print("error: README.md missing CATALOG markers", file=sys.stderr)
        sys.exit(2)
    new_text = pattern.sub(rf"\1\n{catalog}\3", text)
    if new_text == text:
        return False
    README.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    check_mode = "--check" in sys.argv
    skills_by_cat = collect()
    catalog = render(skills_by_cat)

    if check_mode:
        text = README.read_text(encoding="utf-8")
        pattern = re.compile(
            r"<!-- CATALOG:START -->(.*?)<!-- CATALOG:END -->",
            re.DOTALL,
        )
        m = pattern.search(text)
        if not m:
            print("error: README.md missing CATALOG markers", file=sys.stderr)
            return 2
        current = m.group(1).strip("\n")
        expected = catalog.strip("\n")
        if current != expected:
            print("README catalog is out of date. Run: python3 scripts/generate-readme.py", file=sys.stderr)
            return 1
        print("README catalog is up to date.")
        return 0

    changed = update_readme(catalog)
    print("README updated." if changed else "README already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
