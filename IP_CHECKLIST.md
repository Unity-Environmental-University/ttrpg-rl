# IP Classification Checklist

Before pushing to public, verify each file is classified correctly.

## PROPRIETARY (Move to `proprietary/`)

- [ ] `src/constitutional_deck.py`
  - **Why**: Lists the 27 questions that produce 100% pushback
  - **Value**: This is the secret sauce; competitors would want this
  - **Location**: `proprietary/constitutional_deck/constitutional_deck.py`

- [ ] `src/procgen_personas.py`
  - **Why**: Contains the proven persona definitions (Indira, Cassandra, Marcus-2, Athena)
  - **Value**: Shows which question combinations work
  - **Location**: `proprietary/personas/proven_personas.py`

- [ ] `data/matrix/matrix_*.json` (all dialogue files)
  - **Why**: Training data we generated
  - **Value**: Can be fine-tuned on; shows our methodology working
  - **Location**: `proprietary/generated_data/`

- [ ] `SCORING_AUDIT_FINDINGS.md`
  - **Why**: Documents why naive 0-10 scoring fails
  - **Location**: `proprietary/analysis/`

- [ ] `CRITICAL_FINDINGS.md`
  - **Why**: Elena's constitutional questions as template
  - **Location**: `proprietary/analysis/`

- [ ] `BINARY_RUBRIC.md`
  - **Why**: Our calibrated binary rubric (the evaluation moat)
  - **Location**: `proprietary/analysis/binary_rubric.md`

- [ ] `MATRIX_FINDINGS.md`
  - **Why**: Shows that specialists beat generalists, testing obsession wins
  - **Location**: `proprietary/analysis/matrix_findings.md`

- [ ] `VALIDATION_FINDINGS.md`
  - **Why**: Shows pushback rate ≠ learning; our validation approach
  - **Location**: `proprietary/analysis/validation_findings.md`

- [ ] Any `.env` or API keys
  - **Why**: Security
  - **Location**: Never commit; use .gitignore

## PUBLIC (Keep in main repo)

- [ ] `src/dialogue_matrix.py`
  - **Why**: Framework for running systematic tests (not the results)
  - **Expose**: The architecture, not our specific findings

- [ ] `src/dialogue_generator.py`
  - **Why**: Shows how to generate parallel dialogues
  - **Expose**: The pattern for orchestrating personas

- [ ] `src/facilitator.py`
  - **Why**: Shows how to score pedagogical quality
  - **Expose**: The framework, not our calibration

- [ ] `src/scenarios.py`
  - **Why**: Example student scenarios (generic)
  - **Expose**: As template for others to build their own

- [ ] `src/student_profiles.py`
  - **Why**: How to model different student types
  - **Expose**: The framework

- [ ] `data/norms.json`
  - **Why**: Pedagogical principles (publicly defensible)
  - **Expose**: Our philosophy, not our secret findings

- [ ] `tests/`
  - **Why**: Integration tests showing how framework works
  - **Expose**: For transparency

- [ ] `README.md`
  - **Why**: Overview of project and setup
  - **Expose**: Clear separation of public/proprietary

- [ ] `.gitignore`
  - **Why**: Keeps proprietary/ excluded
  - **Expose**: Shows good practice

- [ ] `requirements.txt`
  - **Why**: Dependencies
  - **Expose**: Let others know what to install

## PUBLIC EXAMPLES (Create as stubs)

- [ ] `examples/sample_personas.py`
  - **Template**: Minimal persona definition
  - **Do NOT include**: Our winning personas
  - **Example**:
    ```python
    # Generic example, not a real performer
    example_persona = ProcgenPersona(
        name="MyTeacher",
        question_keys=["listening_1", "testing_1"]
    )
    ```

- [ ] `examples/sample_questions.py`
  - **Template**: How to create constitutional question deck
  - **Do NOT include**: Our 27 questions
  - **Example**:
    ```python
    sample_questions = [
        ConstitutionalQuestion(
            question="Generic example question",
            category=QuestionCategory.LEARNING,
            # etc
        )
    ]
    ```

- [ ] `examples/sample_scenarios.json`
  - **Template**: Student scenario structure
  - **Do NOT include**: Our specific scenarios

## DECISION JOURNAL

Keep in proprietary/analysis/:

- [ ] `decision_journal.md`
  - **Purpose**: Track why we chose each approach
  - **Example entry**:
    ```
    ## Date: 2026-01-15
    ### Decision: Focus on Testing Questions (Indira approach)
    **Why**: Indira achieved 100% pushback by obsessing over
    "Did they demonstrate understanding?"
    **Evidence**: 6/6 dialogues triggered authentic engagement
    **Implication**: Testing > Support > Agency as primary focus
    ```

## Pre-Push Verification

```bash
# Before pushing to public:

# 1. Verify proprietary/ is gitignored
grep "proprietary/" .gitignore

# 2. Check no .py files in public src/ mention constitutional_deck
grep -r "constitutional_deck" src/
grep -r "INDIRA\|CASSANDRA\|ATHENA" src/

# 3. Verify data/matrix is not committed
git status data/matrix/

# 4. List all files that will be pushed
git diff --name-only origin/main

# 5. Manual review of each file
# - Do any .md files reveal IP?
# - Do any comments reference secret findings?
```

## Red Flags

**DO NOT PUSH TO PUBLIC IF:**
- ❌ Filenames mention "secret", "proprietary", "IP", "findings"
- ❌ Comments say "This beats X by Y%"
- ❌ .md files contain analysis like "Indira works 100%"
- ❌ Dialogue files are committed to data/matrix/
- ❌ constitutional_deck.py or procgen_personas.py are in src/
- ❌ Any reference to "80%+ pushback = competitive advantage"
- ❌ Performance comparisons (Indira vs Cassandra vs Rio)

## Approved Public Statements

**CAN say publicly:**
- "We built a framework for testing pedagogical approaches"
- "Constitutional questions shape persona behavior"
- "We test teaching quality systematically"
- "Specialists outperform generalists in our testing"

**DO NOT say publicly:**
- Specific constitutional question text
- Which combinations achieve best results
- Exact pushback rates by persona
- Names and approaches of our top performers
- Specific training data statistics

## Regular Audits

Schedule: Monthly

```bash
# Check for IP leaks
find . -name "*.py" -o -name "*.md" | \
  xargs grep -l "100%\|Indira\|Cassandra\|findings\|secret" | \
  xargs git check-ignore
```

This should show only files in proprietary/ directory (or nothing if all good).
