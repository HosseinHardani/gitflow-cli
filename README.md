# 🚀 Git Automator

A Python CLI tool to automate your daily Git workflows — no more repetitive commands.

## Commands

| Command | What it does |
|--------|--------------|
| `save` | Stage all changes and commit |
| `sync` | Pull then push current branch |
| `feature` | Create a new feature branch from main |
| `undo` | Undo last commit (keeps your changes staged) |
| `cleanup` | Delete all merged branches |
| `status` | Clean, readable status summary |

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/git-automator.git
cd git-automator

# Make it executable
chmod +x git_automator.py

# Optional: add an alias
echo "alias git-auto='python3 $(pwd)/git_automator.py'" >> ~/.bashrc
source ~/.bashrc
```

## Usage

```bash
# Save all changes with a commit message
python3 git_automator.py save -m "feat: add login page"

# Save with auto-generated message
python3 git_automator.py save

# Sync with remote (pull + push)
python3 git_automator.py sync

# Create a new feature branch
python3 git_automator.py feature user-authentication

# Undo last commit (changes stay staged)
python3 git_automator.py undo

# Clean up merged branches
python3 git_automator.py cleanup

# See clean status
python3 git_automator.py status
```

## Requirements

- Python 3.7+
- Git installed and configured

## License

MIT
