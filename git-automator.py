#!/usr/bin/env python3
"""
Git Automator - Automate your daily Git workflows
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime


def run(cmd, capture=True):
    result = subprocess.run(cmd, shell=True, text=True,
                            capture_output=capture)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def check_git_repo():
    _, _, code = run("git rev-parse --git-dir")
    if code != 0:
        print("❌ This is not a git repository.")
        sys.exit(1)


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_save(args):
    """Stage all changes and commit with a message."""
    check_git_repo()

    # Check for changes
    status, _, _ = run("git status --porcelain")
    if not status:
        print("✅ Nothing to commit — working tree clean.")
        return

    msg = args.message or f"chore: auto-save {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    run("git add -A", capture=False)
    out, err, code = run(f'git commit -m "{msg}"')
    if code == 0:
        print(f"✅ Committed: {msg}")
    else:
        print(f"❌ Commit failed:\n{err}")


def cmd_sync(args):
    """Pull latest changes then push local commits."""
    check_git_repo()

    branch, _, _ = run("git rev-parse --abbrev-ref HEAD")
    print(f"🔄 Syncing branch: {branch}")

    print("  ↓ Pulling...")
    out, err, code = run(f"git pull origin {branch}")
    if code != 0:
        print(f"❌ Pull failed:\n{err}")
        return

    print("  ↑ Pushing...")
    out, err, code = run(f"git push origin {branch}")
    if code != 0:
        print(f"❌ Push failed:\n{err}")
        return

    print("✅ Sync complete.")


def cmd_feature(args):
    """Create a new feature branch from main/master."""
    check_git_repo()

    name = args.name.lower().replace(" ", "-")
    branch_name = f"feature/{name}"

    # Find base branch
    _, _, code = run("git rev-parse --verify main")
    base = "main" if code == 0 else "master"

    run(f"git checkout {base}")
    run(f"git pull origin {base}")
    _, err, code = run(f"git checkout -b {branch_name}")

    if code == 0:
        print(f"✅ Created and switched to: {branch_name}")
    else:
        print(f"❌ Failed to create branch:\n{err}")


def cmd_undo(args):
    """Undo the last commit (keeps changes staged)."""
    check_git_repo()

    last_msg, _, _ = run("git log -1 --pretty=%s")
    out, err, code = run("git reset --soft HEAD~1")

    if code == 0:
        print(f"✅ Undid last commit: \"{last_msg}\"")
        print("   Changes are still staged.")
    else:
        print(f"❌ Undo failed:\n{err}")


def cmd_cleanup(args):
    """Delete merged branches (keeps main/master/develop)."""
    check_git_repo()

    protected = {"main", "master", "develop"}
    current, _, _ = run("git rev-parse --abbrev-ref HEAD")

    merged, _, _ = run("git branch --merged")
    branches = [b.strip().lstrip("* ") for b in merged.splitlines()]
    to_delete = [b for b in branches if b and b not in protected and b != current]

    if not to_delete:
        print("✅ No merged branches to clean up.")
        return

    print(f"🧹 Found {len(to_delete)} merged branch(es):")
    for b in to_delete:
        print(f"   - {b}")

    if not args.yes:
        confirm = input("Delete them? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    for b in to_delete:
        _, _, code = run(f"git branch -d {b}")
        status = "✅" if code == 0 else "❌"
        print(f"   {status} Deleted: {b}")


def cmd_status(args):
    """Show a clean, readable status summary."""
    check_git_repo()

    branch, _, _ = run("git rev-parse --abbrev-ref HEAD")
    ahead, _, _ = run("git rev-list @{u}..HEAD --count")
    behind, _, _ = run("git rev-list HEAD..@{u} --count")
    status, _, _ = run("git status --porcelain")

    print(f"📍 Branch : {branch}")
    if ahead and ahead != "0":
        print(f"⬆️  Ahead  : {ahead} commit(s) to push")
    if behind and behind != "0":
        print(f"⬇️  Behind : {behind} commit(s) to pull")

    if status:
        modified = [l for l in status.splitlines() if l.startswith(" M") or l.startswith("M")]
        added    = [l for l in status.splitlines() if l.startswith("A") or l.startswith("??")]
        deleted  = [l for l in status.splitlines() if l.startswith("D") or l.startswith(" D")]

        print(f"\n📂 Changes ({len(status.splitlines())} file(s)):")
        for f in modified: print(f"   ✏️  {f[3:]}")
        for f in added:    print(f"   ➕ {f[3:]}")
        for f in deleted:  print(f"   🗑️  {f[3:]}")
    else:
        print("✅ Working tree clean")


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="git-auto",
        description="🚀 Git Automator — Automate your daily Git workflows"
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    # save
    p_save = sub.add_parser("save", help="Stage all & commit")
    p_save.add_argument("-m", "--message", help="Commit message")
    p_save.set_defaults(func=cmd_save)

    # sync
    p_sync = sub.add_parser("sync", help="Pull then push current branch")
    p_sync.set_defaults(func=cmd_sync)

    # feature
    p_feat = sub.add_parser("feature", help="Create a new feature branch")
    p_feat.add_argument("name", help="Feature name (e.g. 'user-auth')")
    p_feat.set_defaults(func=cmd_feature)

    # undo
    p_undo = sub.add_parser("undo", help="Undo last commit (keeps changes)")
    p_undo.set_defaults(func=cmd_undo)

    # cleanup
    p_clean = sub.add_parser("cleanup", help="Delete merged branches")
    p_clean.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p_clean.set_defaults(func=cmd_cleanup)

    # status
    p_st = sub.add_parser("status", help="Clean status summary")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
