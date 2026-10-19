#!/usr/bin/env python3
"""setup-apc-framework.py — Scaffolds the APC + Local Agent Orchestration Framework into any repository.

Can run interactively or with command-line arguments.
"""

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

FILE_MAPPING = [
    ("AGENTS.md.template", "AGENTS.md"),
    ("docs/context/complete-context.md.template", "docs/context/complete-context.md"),
    ("docs/context/apc-handoff-template.md.template", "docs/context/apc-handoff-template.md"),
    ("docs/context/apc-bundle-quickref.md.template", "docs/context/apc-bundle-quickref.md"),
    ("docs/tasks/status.md.template", "docs/tasks/status.md"),
    ("docs/tasks/high-level-tasks.md.template", "docs/tasks/high-level-tasks.md"),
    ("docs/decisions/decision-log.md.template", "docs/decisions/decision-log.md"),
    ("docs/reports/TASK-TEMPLATE.md.template", "docs/reports/TASK-TEMPLATE.md"),
    ("docs/prompts/STANDALONE-PROMPT-TEMPLATE.md.template", "docs/prompts/STANDALONE-PROMPT-TEMPLATE.md"),
    ("docs/prompts/STANDALONE-ADOPTION-PROMPT.md.template", "docs/prompts/STANDALONE-ADOPTION-PROMPT.md"),
    ("docs/guide/COLLABORATOR-GUIDE.md.template", "docs/guide/COLLABORATOR-GUIDE.md"),
    ("scripts/apc-bundle.sh.template", "scripts/apc-bundle.sh"),
    ("scripts/task-worktree.sh.template", "scripts/task-worktree.sh"),
    ("scripts/validate-report.py.template", "scripts/validate-report.py"),
    ("scripts/manage-decisions.py.template", "scripts/manage-decisions.py"),
    ("scripts/README.md.template", "scripts/README.md"),
]


def prompt_input(prompt_text: str, default_val: str) -> str:
    res = input(f"{prompt_text} [{default_val}]: ").strip()
    return res if res else default_val


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap the APC + Local Agent framework into a repository."
    )
    parser.add_argument("--target-dir", "-t", type=str, help="Target repository directory (default: current directory)")
    parser.add_argument("--project-name", "-n", type=str, help="Human-readable project name")
    parser.add_argument("--project-slug", "-s", type=str, help="Project repository slug (e.g. my-awesome-tool)")
    parser.add_argument("--project-desc", "-d", type=str, help="1-2 sentence project description")
    parser.add_argument("--operator-name", "-o", type=str, help="Human operator name (e.g. Luke)")
    parser.add_argument("--src-dir", type=str, help="Source code directory (default: src)")
    parser.add_argument("--test-cmd", type=str, help="Command to run tests (e.g. pytest, npm test)")
    parser.add_argument("--non-interactive", action="store_true", help="Run without interactive prompts")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files without prompting")
    return parser.parse_args()


def main():
    args = parse_args()

    target_dir = Path(args.target_dir or os.getcwd()).resolve()
    print("=" * 60)
    print("  APC + Local Agent Orchestration Setup")
    print(f"  Target Directory: {target_dir}")
    print("=" * 60)

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    default_slug = target_dir.name
    default_name = default_slug.replace("-", " ").replace("_", " ").title()

    if args.non_interactive:
        project_name = args.project_name or default_name
        project_slug = args.project_slug or default_slug
        project_desc = args.project_desc or f"Core repository for {project_name}."
        operator_name = args.operator_name or os.environ.get("USER", "Operator")
        src_dir = args.src_dir or "src"
        test_cmd = args.test_cmd or "pytest"
    else:
        project_name = args.project_name or prompt_input("Project Name", default_name)
        project_slug = args.project_slug or prompt_input("Project Slug", default_slug)
        project_desc = args.project_desc or prompt_input("Project Description", f"Core repository for {project_name}.")
        operator_name = args.operator_name or prompt_input("Operator Name", os.environ.get("USER", "Operator"))
        src_dir = args.src_dir or prompt_input("Source Code Directory", "src")
        test_cmd = args.test_cmd or prompt_input("Test Runner Command", "pytest")

    placeholders = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_SLUG}}": project_slug,
        "{{PROJECT_DESCRIPTION}}": project_desc,
        "{{OPERATOR_NAME}}": operator_name,
        "{{SRC_DIR}}": src_dir,
        "{{TEST_RUNNER_CMD}}": test_cmd,
    }

    print("\nApplying configuration:")
    for k, v in placeholders.items():
        print(f"  {k:25} -> {v}")

    print("\nCopying and rendering templates...")

    for src_rel, dst_rel in FILE_MAPPING:
        src_path = TEMPLATES_DIR / src_rel
        dst_path = target_dir / dst_rel

        if not src_path.exists():
            print(f"  [ERROR] Template missing: {src_path}", file=sys.stderr)
            continue

        if dst_path.exists() and not args.force:
            if not args.non_interactive:
                overwrite = input(f"  File exists: {dst_rel}. Overwrite? (y/N): ").strip().lower()
                if overwrite != "y":
                    print(f"  [SKIPPED] {dst_rel}")
                    continue
            else:
                print(f"  [SKIPPED] {dst_rel} (exists, use --force to overwrite)")
                continue

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        content = src_path.read_text(encoding="utf-8")
        for key, val in placeholders.items():
            content = content.replace(key, val)

        dst_path.write_text(content, encoding="utf-8")

        # Make scripts executable
        if dst_rel.startswith("scripts/") and (dst_rel.endswith(".sh") or dst_rel.endswith(".py")):
            current_perm = os.stat(dst_path).st_mode
            os.chmod(dst_path, current_perm | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print(f"  [CREATED] {dst_rel}")

    # Generate initial repo-tree.txt if tree command exists
    if shutil.which("tree"):
        os.system(f"cd '{target_dir}' && tree -I '.git|.venv|venv|__pycache__|node_modules|*.tar.gz' --dirsfirst --noreport > docs/context/repo-tree.txt 2>/dev/null || true")

    print("\n" + "=" * 60)
    print("  Framework Setup Complete!")
    print("=" * 60)
    print(f"1. Review 'docs/context/complete-context.md' and customize project sections.")
    print(f"2. Run './scripts/apc-bundle.sh --list' to test bundle configuration.")
    print(f"3. Start your first APC session using 'STANDALONE-ADOPTION-PROMPT.md'.")
    print("=" * 60)


if __name__ == "__main__":
    main()
