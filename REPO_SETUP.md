# Repository Setup Guide

This project uses a public repo + private subrepo pattern to separate open-source framework from proprietary research findings.

## Repository Structure

### Public Repo: `ttrpg-rl`
- **Visibility**: Public (GitHub)
- **Contains**: Framework code, examples, methodology
- **Purpose**: Help others build similar pedagogical AI systems
- **License**: MIT or Apache 2.0 (TBD)

### Private Repo: `ttrpg-rl-proprietary`
- **Visibility**: Private (GitHub)
- **Contains**: Constitutional questions deck, proven personas, findings, training data
- **Purpose**: Competitive advantage and IP protection
- **Integrated as**: Git submodule in `proprietary/` directory

## First-Time Setup

### 1. Create GitHub Repositories

Using `gh` CLI (already logged in):

```bash
# Create public repo
gh repo create ttrpg-rl \
  --public \
  --description "Framework for pedagogically-aligned training data generation" \
  --org UNIVERSITY-ORG

# Create private repo
gh repo create ttrpg-rl-proprietary \
  --private \
  --description "Proprietary: Constitutional questions, proven personas, findings" \
  --org UNIVERSITY-ORG
```

### 2. Initialize Public Repo

```bash
cd /Users/hallie/Documents/repos/unity/ttrpg-rl

git add .gitignore README.md .gitmodules requirements.txt
git commit -m "Initial commit: Framework architecture and setup"

git remote add origin git@github.com:UNIVERSITY-ORG/ttrpg-rl.git
git branch -M main
git push -u origin main
```

### 3. Initialize Private Subrepo

```bash
mkdir -p proprietary

cd proprietary
git init
git remote add origin git@github.com:UNIVERSITY-ORG/ttrpg-rl-proprietary.git

# Create initial files in proprietary repo
touch .gitkeep
git add .gitkeep
git commit -m "Initial commit: Proprietary layer placeholder"
git branch -M main
git push -u origin main

cd ..
```

### 4. Add Subrepo to Main Repo

```bash
git submodule add git@github.com:UNIVERSITY-ORG/ttrpg-rl-proprietary.git proprietary

git add .gitmodules proprietary
git commit -m "Add proprietary submodule"
git push origin main
```

## Ongoing Workflow

### Committing to Public Repo

```bash
# Make changes to src/, tests/, examples/, data/norms.json, etc.
git add .
git commit -m "Add feature: [description]"
git push origin main
```

### Committing to Proprietary Subrepo

```bash
# Make changes in proprietary/
cd proprietary
git add .
git commit -m "Add: Constitutional question deck v0.2"
git push origin main

# Return to main repo and update submodule reference
cd ..
git add proprietary
git commit -m "Update proprietary submodule"
git push origin main
```

### Cloning This Repo (with Subrepo)

```bash
# Clone main repo
git clone git@github.com:UNIVERSITY-ORG/ttrpg-rl.git

# Initialize and fetch submodule
cd ttrpg-rl
git submodule init
git submodule update

# Or in one step on clone:
git clone --recurse-submodules git@github.com:UNIVERSITY-ORG/ttrpg-rl.git
```

## Protecting IP

### Files That Should NEVER Be Public

**Move these to `proprietary/` immediately:**
- `src/constitutional_deck.py` → `proprietary/constitutional_deck/`
- `src/procgen_personas.py` → `proprietary/personas/`
- `data/matrix/*.json` (all generated dialogues) → `proprietary/generated_data/`
- Any analysis findings → `proprietary/analysis/`

### Before First Push to Public

```bash
# 1. Move proprietary files
mv src/constitutional_deck.py proprietary/constitutional_deck/
mv src/procgen_personas.py proprietary/personas/
mv data/matrix/ proprietary/generated_data/

# 2. Create public examples
cp proprietary/constitutional_deck/example_template.py examples/sample_questions.py
cp proprietary/personas/example_definition.py examples/sample_personas.py

# 3. Verify .gitignore is correct
cat .gitignore | grep proprietary/

# 4. Commit proprietary stuff
cd proprietary
git add .
git commit -m "Add constitutional deck and proven personas"
git push origin main

# 5. Commit public repo (which now excludes proprietary/)
cd ..
git add examples/
git commit -m "Add public examples and setup docs"
git push origin main
```

## GitHub Access Control

### For University Org Members

**Can access:**
- `ttrpg-rl` (public) - Anyone on internet
- `ttrpg-rl-proprietary` (private) - Team members with explicit access

**Setup team access:**

```bash
# Add team to private repo
gh repo edit UNIVERSITY-ORG/ttrpg-rl-proprietary \
  --add-team "research-team"
```

## Troubleshooting

**"fatal: unable to access proprietary... Permission denied"**
- Make sure SSH key is configured: `ssh -T git@github.com`
- Check you have access to private repo

**Submodule not updating**
```bash
git submodule sync --recursive
git submodule update --recursive --remote
```

**Need to create a fresh clone without proprietary?**
```bash
# Clone without submodule
git clone git@github.com:UNIVERSITY-ORG/ttrpg-rl.git --no-checkout

# Later, add submodule
git submodule init
```

## References

- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub Private Repos](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
