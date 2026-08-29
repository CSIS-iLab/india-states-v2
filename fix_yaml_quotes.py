#!/usr/bin/env python3
"""
Fix unclosed/broken single-quoted strings in YAML frontmatter of Markdown files.

Handles values that:
  - span multiple lines before a lone closing ' on its own line
  - are wrapped across continuation lines (indented) before a lone '
  - simply have no closing quote at all

Does NOT touch values that are already valid YAML (e.g. properly wrapped
multi-line strings that end with a closing quote on a continuation line).

Usage:
    python3 fix_yaml_quotes.py                  # Fix all .md files in current directory
    python3 fix_yaml_quotes.py path/to/dir      # Fix all .md files in a specific directory
    python3 fix_yaml_quotes.py file.md          # Fix a single file
    python3 fix_yaml_quotes.py --dry-run ...    # Preview without modifying
"""

import sys
import os
import re
import glob


def get_indent(line: str) -> int:
    """Return number of leading spaces in a line."""
    return len(line) - len(line.lstrip(" "))


def is_new_yaml_key(line: str, open_indent: int) -> bool:
    """
    Return True if this line starts a new YAML key/list item at the same or
    lower indentation than the opening line — meaning it's NOT a continuation.
    """
    stripped = line.strip()
    if not stripped:
        return False  # blank lines are not new keys
    indent = get_indent(line)
    if indent > open_indent:
        return False  # more indented = continuation
    # Same or lower indent: check if it looks like a key or list marker
    return bool(re.match(r"^(\s*[\w\-]+\s*:|\s*-\s)", line))


def fix_frontmatter(frontmatter: str) -> tuple[str, int]:
    """
    Fix broken single-quoted YAML values in frontmatter text.
    Works line-by-line using a small state machine.
    Returns (fixed_frontmatter, number_of_fixes).
    """
    lines = frontmatter.split("\n")
    out = []
    fixes = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Match a line that opens a single-quoted value
        # Handles: "- key: 'value", "  key: 'value", "  - 'value"
        m = re.match(
            r"^(\s*-\s+[\w\-]+\s*:[ \t]*|[^\S\n]*[\w\-]+\s*:[ \t]*|[^\S\n]*-[ \t]*)'(.*)",
            line,
        )

        if m:
            prefix = m.group(1)
            value_on_open_line = m.group(2).rstrip()
            open_indent = get_indent(line)

            # Check if the value is already properly closed on this line
            # A value like 'foo' is closed; 'foo is not; '' is closed (empty)
            if value_on_open_line.endswith("'"):
                # Already closed — leave it alone
                out.append(line)
                i += 1
                continue

            # Value is not closed on the opening line — look ahead
            value_parts = [value_on_open_line] if value_on_open_line else []
            i += 1
            found_close = False

            while i < len(lines):
                cont = lines[i]
                stripped = cont.strip()

                # A lone ' on its own line = stray closing quote → stop
                if stripped == "'":
                    i += 1
                    found_close = True
                    break

                # A new YAML key/list at same or lower indent = not a continuation
                if is_new_yaml_key(cont, open_indent):
                    # Don't consume this line — it belongs to the next key
                    break

                # Blank line inside a broken value — skip
                if stripped == "":
                    i += 1
                    continue

                # Continuation content line
                # If it ends with ' it might be a valid wrapped closing — check:
                # A properly wrapped YAML continuation that closes the quote looks like
                # "  the state '" — ends with quote after real content.
                if stripped.endswith("'") and len(stripped) > 1:
                    # This continuation line closes the value properly
                    value_parts.append(stripped.rstrip("'").rstrip())
                    i += 1
                    found_close = True
                    break

                value_parts.append(stripped)
                i += 1

            combined = " ".join(p for p in value_parts if p)
            out.append(f"{prefix}'{combined}'")
            fixes += 1
        else:
            out.append(line)
            i += 1

    return "\n".join(out), fixes


def fix_file_text(text: str) -> tuple[str, int]:
    """Fix a full markdown file's YAML frontmatter."""
    if not text.startswith("---"):
        return text, 0

    match = re.match(r"^---\n(.*?\n)---(\n|$)", text, re.DOTALL)
    if not match:
        return text, 0

    frontmatter = match.group(1)
    rest = text[match.end():]

    fixed_fm, fixes = fix_frontmatter(frontmatter)
    return f"---\n{fixed_fm}---\n{rest}", fixes


def process_file(filepath: str, dry_run: bool = False) -> bool:
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    fixed, fixes = fix_file_text(original)

    if fixes == 0:
        print(f"  ✓ No issues: {filepath}")
        return False

    if dry_run:
        print(f"  ~ Would fix {fixes} value(s) in: {filepath}")
        return True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"  ✅ Fixed {fixes} value(s) in: {filepath}")
    return True


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if dry_run:
        print("🔍 Dry run — no files will be modified.\n")

    target = args[0] if args else "."

    if os.path.isfile(target):
        md_files = [target]
    elif os.path.isdir(target):
        md_files = glob.glob(os.path.join(target, "**", "*.md"), recursive=True)
    else:
        print(f"Error: '{target}' is not a valid file or directory.")
        sys.exit(1)

    if not md_files:
        print("No .md files found.")
        sys.exit(0)

    print(f"Processing {len(md_files)} file(s)...\n")
    changed = sum(process_file(f, dry_run=dry_run) for f in sorted(md_files))
    print(f"\nDone. {changed}/{len(md_files)} file(s) {'would be ' if dry_run else ''}updated.")


if __name__ == "__main__":
    main()
