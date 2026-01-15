# Setup Complete ✓

Both repositories are now live on GitHub and linked via submodule.

## Repository Status

### Public Repo ✓
- **URL**: https://github.com/Unity-Environmental-University/ttrpg-rl
- **Visibility**: Public
- **Content**: Framework code, documentation, setup guides
- **Status**: Initial commit pushed

### Private Subrepo ✓
- **URL**: https://github.com/Unity-Environmental-University/ttrpg-rl-proprietary
- **Visibility**: Private
- **Content**: Constitutional questions, proven personas, findings, training data
- **Status**: Initialized and linked

## What's in Each Repo Right Now

### Public (ttrpg-rl)
```
✓ .gitignore                    # Excludes Python artifacts, .env, data generation
✓ .gitmodules                   # Points to proprietary subrepo
✓ README.md                     # Project overview + public/proprietary split
✓ REPO_SETUP.md                 # How to work with the repo
✓ IP_CHECKLIST.md               # Which files are proprietary
✓ SETUP_COMPLETE.md             # This file
✓ requirements.txt              # Dependencies
✓ src/                          # Framework code (not yet committed, see below)
✓ data/norms.json               # Pedagogical boundaries
```

### Private (ttrpg-rl-proprietary)
```
✓ README.md                     # Placeholder
```

## Next Steps: Move Proprietary Files

These files should be moved to the private subrepo **BEFORE public use**:

```bash
# 1. Move to proprietary/
mv src/constitutional_deck.py proprietary/constitutional_deck/
mv src/procgen_personas.py proprietary/personas/
mv data/matrix/ proprietary/generated_data/

# 2. Move analysis docs
mv SCORING_AUDIT_FINDINGS.md proprietary/analysis/
mv CRITICAL_FINDINGS.md proprietary/analysis/
mv BINARY_RUBRIC.md proprietary/analysis/
mv MATRIX_FINDINGS.md proprietary/analysis/
mv VALIDATION_FINDINGS.md proprietary/analysis/

# 3. Commit to proprietary subrepo
cd proprietary
git add constitutional_deck/ personas/ generated_data/ analysis/
git commit -m "Add constitutional deck, proven personas, analysis, training data"
git push origin main

# 4. Return and update main repo reference
cd ..
git add proprietary/
git commit -m "Update proprietary subrepo with IP"
git push origin main
```

## Cloning the Repository (for others)

**Full clone (with proprietary submodule):**
```bash
git clone --recurse-submodules \
  https://github.com/Unity-Environmental-University/ttrpg-rl.git
```

**Clone without proprietary (public-only):**
```bash
git clone https://github.com/Unity-Environmental-University/ttrpg-rl.git
# (Proprietary/ directory will be empty)
```

**Update submodule later:**
```bash
cd ttrpg-rl
git submodule init
git submodule update
```

## File Organization Guide

### Public Repo (what gets open-sourced)
```
src/
  ├── dialogue_generator.py       # Orchestration pattern
  ├── dialogue_matrix.py          # Testing framework
  ├── facilitator.py              # Scoring framework
  ├── scenarios.py                # Example scenarios
  ├── student_responses.py        # Response generation
  └── student_profiles.py         # Student modeling

examples/
  ├── sample_personas.py          # Template (not our winners)
  ├── sample_questions.py         # Template (not our questions)
  └── sample_scenarios.json       # Template scenarios

tests/
  └── test_framework.py           # Verify framework works

data/
  └── norms.json                  # Pedagogical principles

README.md                          # What this is
REPO_SETUP.md                      # How to use it
IP_CHECKLIST.md                    # What's proprietary
requirements.txt                   # Dependencies
```

### Private Subrepo (competitive advantage)
```
proprietary/
  ├── constitutional_deck/        # The 27 questions
  ├── personas/                   # Proven personas (Indira, Cassandra, Marcus-2, Athena)
  ├── generated_data/             # All 48+ training dialogues
  └── analysis/
      ├── MATRIX_FINDINGS.md      # Which approaches work
      ├── VALIDATION_FINDINGS.md  # Binary rubric correlation
      ├── binary_rubric.md        # Our calibrated rubric
      └── decision_journal.md     # Why each choice
```

## Security Checklist

Before first use:

- [ ] Verify .gitignore excludes `*.env` and `*.key`
- [ ] Confirm proprietary/ is private on GitHub (Settings → Visibility)
- [ ] Check README doesn't mention specific findings
- [ ] Run `git status` to ensure no secrets are staged
- [ ] Verify team access to private repo: https://github.com/orgs/Unity-Environmental-University/teams

## Working Locally

```bash
# Update both repos
git pull origin main                    # Update public
cd proprietary && git pull origin main  # Update private

# Make changes in public repo
# ... edit src/*, add docs, etc ...
git add .
git commit -m "..."
git push origin main

# Make changes in proprietary
cd proprietary
# ... edit constitutional deck, personas, etc ...
git add .
git commit -m "..."
git push origin main

# Back to main repo (update submodule reference)
cd ..
git add proprietary/
git commit -m "Update proprietary layer"
git push origin main
```

## Visibility Rules

### Safe to Commit to Public
- Framework code that describes the pattern, not results
- Generic examples and templates
- Methodology documentation
- Philosophy and principles
- Test code and setup documentation

### NEVER Commit to Public
- The actual constitutional questions (constitutional_deck.py)
- The winning personas (procgen_personas.py)
- Generated dialogue files (data/matrix/*.json)
- Analysis findings (which approaches work, percentages, correlations)
- Performance comparisons (Indira 100%, Cassandra 83%, etc.)

## Workflow Example: Adding a New Feature

```bash
# 1. Create feature in public framework
git checkout -b feature/add-new-scorer

# Edit src/facilitator.py (public code)
vim src/facilitator.py

# Test it
python tests/test_framework.py

# Commit
git add src/facilitator.py
git commit -m "Add new scoring metric to facilitator"
git push origin feature/add-new-scorer

# Create PR, review, merge

# 2. Test with proprietary data
cd proprietary
python ../src/facilitator.py generated_data/sample_dialogue.json

# 3. If private data improves results, update analysis
vim analysis/decision_journal.md
git add analysis/decision_journal.md
git commit -m "Update findings: new scorer improves detection by X%"
git push origin main

# 4. Back to public repo, update submodule reference
cd ..
git add proprietary/
git commit -m "Update proprietary with new findings"
git push origin main
```

## Questions?

Refer to:
- `REPO_SETUP.md` - Full setup instructions
- `IP_CHECKLIST.md` - What's proprietary vs. public
- GitHub wiki (can be enabled if needed)

---

**Summary**: Public framework + private findings = open innovation without giving away competitive advantage.
